#!/bin/bash


LIBMLX4='libmlx4'
LIBIBVERBS='libibverbs'
LIBRTEPMD='librte_pmd_mlx4'

usage()
{
	echo "./compile_mlx4_pmd.sh " \
		"-s <RTE_SDK> " \
		"-t <RTE_TARGET> " \
		"[ -r (enable receive inline)]" \
		"[ -c (enable HW checksum offloading) ] ]" \
		"[ -m (enable multi-segment send / recv messages ) " \
		"[ -d (debug) ] "
}

if [ $# -le 1 ]
then
	usage
        exit
fi

RTE_SDK="NULL"
RTE_TARGET="NULL"

DEBUG=0
SGE_WR_N=1
PROMISC_OPT=0
CSUM=0
MLX4_CSUM="--without-dpdk-rx-csum"
MLX4_INLINE_RX="--without-dpdk-inline-recv"

while getopts ":hs:t:rmcd" OPTION
do
	case $OPTION in
		h)
				usage
				exit 1
				;;
		s)
				RTE_SDK=$OPTARG
				;;
		t)
				RTE_TARGET=$OPTARG
				;;
		r)
				MLX4_INLINE_RX="--with-dpdk-inline-recv"
				;;
		m)
				SGE_WR_N=4
				;;
		c)
				CSUM=1
				MLX4_CSUM="--with-dpdk-rx-csum"
				;;
		d)
				DEBUG=1
				;;
		?)
				echo "Invalid option"
				usage
				exit 1
				;;
		esac
done

if [ "$RTE_SDK" == "NULL" ] || [ "$RTE_TARGET" == "NULL" ]
then
	usage
	exit
fi


echo "Entering: " $LIBIBVERBS
cd $LIBIBVERBS

make -s clean
./autogen.sh
ac_cv_asm_symver_support=no ./configure --silent --with-dpdk --disable-examples --disable-shared --enable-static --without-resolve-neigh  CFLAGS='-O3 -fPIC -g -fno-omit-frame-pointer' CPPFLAGS='-Iinclude'
ac_cv_asm_symver_support=no make
if [ $? -ne 0 ]
then
	echo "Failed to compile $LIBIBVERBS"
	exit
fi


cd -
echo "Entering: " $LIBMLX4
cd $LIBMLX4

make -s clean
./autogen.sh
./configure --silent --with-dpdk $MLX4_INLINE_RX $MLX4_CSUM --disable-shared --enable-static CFLAGS="-O3 -fPIC -g -fno-omit-frame-pointer" CPPFLAGS="-I../"$LIBIBVERBS"/include/" LIBS="-pthread -ldl"
make -s
if [ $? -ne 0 ]
then
	echo "Failed to compile $LIBMLX4"
	exit
fi


cd - 
echo "Entering: " $LIBRTEPMD
cd $LIBRTEPMD
RTE_SDK=$RTE_SDK  RTE_TARGET=$RTE_TARGET make -s clean

CFLAGS='-I../'$LIBIBVERBS'/include -g -fno-omit-frame-pointer'  LDFLAGS='-L../'$LIBMLX4'/src/.libs -L../'$LIBIBVERBS'/src/.libs -pthread -ldl'  LIBS='-Wl,--whole-archive -lmlx4 -Wl,--no-whole-archive' \
	make RTE_SDK=$RTE_SDK  RTE_TARGET=$RTE_TARGET OPT_CQ=1 MLX4_PMD_SGE_WR_N=$SGE_WR_N DEBUG=$DEBUG CSUM=$CSUM

if [ $? -ne 0 ]
then
        echo "Failed to compile $LIBRTEPMD"
        exit
fi

