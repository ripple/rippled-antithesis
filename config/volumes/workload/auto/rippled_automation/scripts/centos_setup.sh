#!/usr/bin/env bash
set -ex

yum -y upgrade
yum -y update
yum -y install epel-release centos-release-scl
yum -y install \
    wget curl time gcc-c++ time yum-utils \
    devtoolset-4 devtoolset-4-gdb devtoolset-4-libasan-devel devtoolset-4-libtsan-devel devtoolset-4-libubsan-devel \
    devtoolset-6 devtoolset-6-gdb devtoolset-6-libasan-devel devtoolset-6-libtsan-devel devtoolset-6-libubsan-devel \
    devtoolset-7 devtoolset-7-gdb devtoolset-7-libasan-devel devtoolset-7-libtsan-devel devtoolset-7-libubsan-devel \
    llvm-toolset-7 llvm-toolset-7-runtime llvm-toolset-7-build llvm-toolset-7-clang \
    llvm-toolset-7-clang-analyzer llvm-toolset-7-clang-devel llvm-toolset-7-clang-libs \
    llvm-toolset-7-clang-tools-extra llvm-toolset-7-compiler-rt llvm-toolset-7-lldb \
    llvm-toolset-7-lldb-devel llvm-toolset-7-python-lldb \
    flex flex-devel bison bison-devel \
    ncurses ncurses-devel ncurses-libs graphviz graphviz-devel \
    lzip p7zip bzip2 \
    zlib zlib-devel zlib-static texinfo \
    libicu-devel htop \
    python27-python rh-python35-python \
    python-devel python27-python-devel rh-python35-python-devel \
    python27 rh-python35 \
    cmake3 ninja-build git svn \
    protobuf protobuf-static protobuf-c-devel \
    protobuf-compiler protobuf-devel \
    swig ccache perl-Digest-MD5 python2-pip \
    xauth xterm mesa-libGL-devel xorg-x11-server-Xvfb

yum -y install https://github.com/linux-test-project/lcov/releases/download/v1.13/lcov-1.13-1.noarch.rpm
# TODO need permanent link
# yum -y install https://rpmfind.net/linux/fedora/linux/updates/26/x86_64/Packages/p/python2-six-1.10.0-9.fc26.noarch.rpm
yum -y install ftp://ftp.pbone.net/mirror/archive.fedoraproject.org/fedora-secondary/updates/26/i386/Packages/p/python2-six-1.10.0-9.fc26.noarch.rpm

alias cmake="$(which cmake3)"

pip install requests
pip install https://github.com/codecov/codecov-python/archive/master.zip

set +e
source scl_source enable devtoolset-6 python27
set -e

pip install requests
pip install https://github.com/codecov/codecov-python/archive/master.zip

cd /tmp
wget https://ftp.gnu.org/gnu/gdb/gdb-8.0.1.tar.xz
tar xvf gdb-8.0.1.tar.xz
cd gdb-8.0.1
./configure CFLAGS="-w -O2" CXXFLAGS="-std=gnu++11 -g -O2 -w" --prefix=/opt/local/gdb-8.0
make -j$(nproc)
make install
ln -s /opt/local/gdb-8.0 /opt/local/gdb
cd ..
rm -f gdb-8.0.1.tar.xz
rm -rf gdb-8.0.1

cd /tmp
OPENSSL_VER=1.1.1
wget https://www.openssl.org/source/openssl-${OPENSSL_VER}.tar.gz
tar xvf openssl-${OPENSSL_VER}.tar.gz
cd openssl-${OPENSSL_VER}
./config -fPIC --prefix=/usr/local --openssldir=/usr/local/openssl zlib shared -g
make -j$(nproc)
make install
cd ..
rm -f openssl-${OPENSSL_VER}.tar.gz
rm -rf openssl-${OPENSSL_VER}

cd /tmp
wget https://github.com/doxygen/doxygen/archive/Release_1_8_14.tar.gz
tar xvf Release_1_8_14.tar.gz
cd doxygen-Release_1_8_14
mkdir build
cd build
cmake -G "Unix Makefiles" ..
make -j$(nproc)
make install
cd ../..
rm -f Release_1_8_14.tar.gz
rm -rf doxygen-Release_1_8_14

cd /tmp
wget https://download.libsodium.org/libsodium/releases/LATEST.tar.gz
tar xvf LATEST.tar.gz
cd libsodium-stable
./configure --prefix=/usr/local
make -j$(nproc) && make check
make install
cd ..
rm -f LATEST.tar.gz
rm -rf libsodium-stable

mkdir -p /opt/plantuml
wget -O /opt/plantuml/plantuml.jar http://sourceforge.net/projects/plantuml/files/plantuml.jar/download

# clang from source
RELEASE=tags/RELEASE_700/final
INSTALL=/opt/llvm-7.0.0/
mkdir -p /tmp/clang-src
cd /tmp/clang-src
TOPDIR=`pwd`
svn co http://llvm.org/svn/llvm-project/llvm/${RELEASE} llvm
cd ${TOPDIR}/llvm/tools
svn co http://llvm.org/svn/llvm-project/cfe/${RELEASE} clang
cd ${TOPDIR}/llvm/tools/clang/tools
svn co http://llvm.org/svn/llvm-project/clang-tools-extra/${RELEASE} extra
cd ${TOPDIR}/llvm/tools
svn co http://llvm.org/svn/llvm-project/lld/${RELEASE} lld
cd ${TOPDIR}/llvm/tools
svn co http://llvm.org/svn/llvm-project/polly/${RELEASE} polly
cd ${TOPDIR}/llvm/projects
svn co http://llvm.org/svn/llvm-project/compiler-rt/${RELEASE} compiler-rt
cd ${TOPDIR}/llvm/projects
svn co http://llvm.org/svn/llvm-project/openmp/${RELEASE} openmp
cd ${TOPDIR}/llvm/projects
svn co http://llvm.org/svn/llvm-project/libcxx/${RELEASE} libcxx
svn co http://llvm.org/svn/llvm-project/libcxxabi/${RELEASE} libcxxabi
cd ${TOPDIR}/llvm/projects
## config/build
cd ${TOPDIR}
mkdir mybuilddir && cd mybuilddir
cmake ../llvm -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=${INSTALL} \
  -DLLVM_LIBDIR_SUFFIX=64 \
  -DLLVM_ENABLE_EH=ON \
  -DLLVM_ENABLE_RTTI=ON
cmake --build . --parallel
# check-all doesn't pass for me
#cmake --build . --parallel --target check-all
cmake --build . --parallel --target check-clang
cmake --build . --parallel --target install
cd /tmp
rm -rf clang-src

mkdir -p /opt/local/nih_cache

function build_boost()
{
	local boost_ver=$1
    local do_link=$2
    local boost_path=$(echo "${boost_ver}" | sed -e 's!\.!_!g')
    cd /tmp
    wget https://dl.bintray.com/boostorg/release/${boost_ver}/source/boost_${boost_path}.tar.bz2
    mkdir -p /opt/local
    cd /opt/local
    tar xvf /tmp/boost_${boost_path}.tar.bz2
    if [ "$do_link" = true ] ; then
        ln -s ./boost_${boost_path} boost
    fi
    cd boost_${boost_path}
    ./bootstrap.sh
    ./b2 -j$(nproc)
    ./b2 stage
    cd ..
    rm -f /tmp/boost_${boost_path}.tar.bz2
}

build_boost "1.71.0" true
build_boost "1.70.0" false

cd /tmp
CM_INSTALLER=cmake-3.12.3-Linux-x86_64.sh
CM_VER_DIR=/opt/local/cmake-3.12
wget https://cmake.org/files/v3.12/$CM_INSTALLER
chmod a+x $CM_INSTALLER
mkdir -p $CM_VER_DIR
ln -s $CM_VER_DIR /opt/local/cmake
./$CM_INSTALLER --prefix=$CM_VER_DIR --exclude-subdir
rm -f /tmp/$CM_INSTALLER

set +e

mkdir -p /opt/jenkins
set -e

exit 0

