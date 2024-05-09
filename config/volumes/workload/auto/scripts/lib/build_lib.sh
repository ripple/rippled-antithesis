#!/usr/bin/env sh

################################################################################
# This lib includes all methods to support rippled build, like
# gcc, cmake, conan, rippled build, etc
################################################################################

profile_path="${HOME}/.profile"
cmake_version=3.22.3
gcc_version=12
abi_version=11
cppstd=20

update_gcc() {
  echo "Updating gcc to v${gcc_version}..."
  log_file="${log_dir}/gcc.log"

  CWD=$(pwd)
  apt-get update -y >> "${log_file}" 2>&1 && \
  apt-get dist-upgrade -y >> "${log_file}" 2>&1 && \
  apt-get install build-essential software-properties-common -y >> "${log_file}" 2>&1 && \
  add-apt-repository ppa:ubuntu-toolchain-r/test -y >> "${log_file}" 2>&1 && \
  apt-get update -y >> "${log_file}" 2>&1
  update-alternatives --force --remove-all gcc >> "${log_file}" 2>&1
  apt-get install gcc-${gcc_version} g++-${gcc_version} -y >> "${log_file}" 2>&1
  exit_on_error $? "Failed to install gcc-${gcc_version}"
  update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-${gcc_version} 60 --slave /usr/bin/g++ g++ /usr/bin/g++-${gcc_version} >> "${log_file}" 2>&1 && \
  update-alternatives --config gcc >> "${log_file}" 2>&1

  gcc --version
  cd "${CWD}"
}

install_cmake() {
  CWD=$(pwd)
  echo "Install cmake..."
  cd "${work_dir}"
  wget -q https://github.com/Kitware/CMake/releases/download/v"${cmake_version}"/cmake-"${cmake_version}"-Linux-x86_64.sh
  exit_on_error $?
  sh cmake-"${cmake_version}"-Linux-x86_64.sh --prefix=/usr/local --exclude-subdir
  exit_on_error $? "Failed to install cmake-${cmake_version}"

  cmake --version
  exit_on_error $? "Failed to install cmake-${cmake_version}"
  cd "${CWD}"
}

install_conan() {
  echo "Preparing prereq for building witness on ubuntu..."
  pip install --upgrade 'conan<2' > "${log_dir}/conan_setup.log" 2>&1

  conan profile new default --detect >> "${log_dir}/conan_setup.log" 2>&1
  conan profile update settings.compiler.cppstd=${cppstd} default >> "${log_dir}/conan_setup.log" 2>&1
  conan profile update settings.compiler.libcxx=libstdc++${abi_version} default >> "${log_dir}/conan_setup.log" 2>&1
}

prereq_for_building_on_ubuntu() {
  if [ ! "${ignore_rippled_build_prereq}" = "true" ] ; then
    echo "Preparing prereq for building ${product} on ubuntu..."
    update_gcc
    install_cmake
    install_conan
  else
    echo "Skipping prereq installs like cmake, conan, etc"
  fi
}

build_rippled_on_ubuntu() {
  echo "Building rippled on ubuntu..."

  CWD=$(pwd)
  cd "${local_rippled_repo_path}"
  conan export external/snappy snappy/1.1.9@ > "${log_dir}/snappy.log" 2>&1
  conan export external/soci soci/4.0.3@ > "${log_dir}/soci.log" 2>&1
  exit_on_error $?

  mkdir -p "${rippled_build_path}" ; cd "${rippled_build_path}"
  conan install .. --output-folder . --build missing --settings build_type=Release > "${log_dir}/conan_install.log" 2>&1
  exit_on_error $? "conan install failed"

  cmake -DCMAKE_TOOLCHAIN_FILE:FILEPATH=build/generators/conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release .. > "${log_dir}/cmake_build.log" 2>&1
  exit_on_error $? "cmake failed"

  cmake --build . -- -j $(nproc) >> "${log_dir}/cmake_build.log" 2>&1
  exit_on_error $? "rippled build failed"

  echo "Copy rippled binary to ${rippled_exec}..."
  mkdir -p $(dirname "${rippled_exec}")
  cp "${rippled_build_path}/rippled" "${rippled_exec}"

  cd "${CWD}"
}

clone_witness_repo() {
    CWD=$(pwd)
    git clone "${witness_repo_url}" "${local_witness_repo_path}"
    cd "${local_witness_repo_path}"
    git checkout "${witness_checkout_branch}"
    exit_on_error $? "Failed to checkout branch: ${witness_checkout_branch}"
    git log -1
    cd "${CWD}"
}

build_witness_on_ubuntu() {
  echo "Building witness on ubuntu..."

  CWD=$(pwd)
  . "${profile_path}"
  mkdir -p "${witness_build_path}" ; cd "${witness_build_path}"

  conan remote add --insert 0 conan-non-prod http://18.143.149.228:8081/artifactory/api/conan/conan-non-prod
  exit_on_error $? "Adding conan-non-prod repository failed"

  conan install .. --output-folder . --build missing --settings build_type=Release > "${log_dir}/witness_conan.log" 2>&1
  exit_on_error $? "conan install failed"

  cmake -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release .. > "${log_dir}/witness_cmake.log" 2>&1
  exit_on_error $? "cmake failed"

  cmake --build . -- -j $(nproc) > "${log_dir}/witness_make.log" 2>&1
  exit_on_error $? "witness build failed"

  echo "Copy witness binary to ${witness_exec}..."
  mkdir -p $(dirname "${witness_exec}")
  cp "${witness_build_path}/xbridge_witnessd" "${witness_exec}"

  cd "${CWD}"
}

build_clio_on_ubuntu() {
  echo "Building clio on ubuntu..."

  CWD=$(pwd)
  cd "${local_clio_repo_path}"
  conan remote add --insert 0 conan-non-prod http://18.143.149.228:8081/artifactory/api/conan/conan-non-prod > "${log_dir}/conan-non-prod-artifactory.log" 2>&1
  conan remove -f xrpl > "${log_dir}/conan_remove_xrpl.log" 2>&1
  exit_on_error $?

  mkdir -p "${clio_build_path}" ; cd "${clio_build_path}"
  conan install .. --output-folder . --build missing --settings build_type=Release -o tests=True -o lint=False > "${log_dir}/clio_conan_install.log" 2>&1
  exit_on_error $? "conan install failed"

  cmake -DCMAKE_TOOLCHAIN_FILE:FILEPATH=build/generators/conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release .. > "${log_dir}/${product}_cmake_build.log" 2>&1
  exit_on_error $? "cmake failed"

  cmake --build . --parallel $(nproc) >> "${log_dir}/${product}_cmake_build.log" 2>&1
  exit_on_error $? "clio build failed"

  echo "Copy clio binary to ${clio_exec}..."
  mkdir -p $(dirname "${clio_exec}")
  cp "${clio_build_path}/clio_server" "${clio_exec}"

  cd "${CWD}"
}

setup_db_for_clio() {
  echo "Setting up Cassandra db for clio..."
  CWD=$(pwd)

  apt -y update  > "${log_dir}/apt_update.log" 2>&1
  exit_on_error $? "apt update failed"

  apt -y install openjdk-11-jdk  > "${log_dir}/install_jdk.log" 2>&1
  exit_on_error $? "install jdk failed"

  java -version  > "${log_dir}/java_version.log" 2>&1
  exit_on_error $? "failed to get installed java version"

  apt -y install curl > "${log_dir}/install_curl.log" 2>&1
  exit_on_error $? "install curl failed"

  echo "deb https://debian.cassandra.apache.org 41x main" | tee -a /etc/apt/sources.list.d/cassandra.sources.list
  exit_on_error $? "adding cassandra to sources list failed"

  curl https://downloads.apache.org/cassandra/KEYS | apt-key add -  > "${log_dir}/download_cassandra.log" 2>&1
  exit_on_error $? "cassandra download failed"

  apt-get -y update  > "${log_dir}/apt_update.log" 2>&1
  exit_on_error $? "apt-get failed"

  apt-get -y install cassandra  > "${log_dir}/install_cassandra.log" 2>&1
  exit_on_error $? "install cassandra failed"

  cassandra -R  > "${log_dir}/start_cassandra.log" 2>&1 &
  exit_on_error $? "start cassandra failed"

  echo "Set up Cassandra db for clio is done"
}

