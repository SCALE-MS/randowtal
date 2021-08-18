. $ROOT/scripts/common.sh
. $VENV/bin/activate
. $PROJECT/gromacs2021/bin/GMXRC
pushd gromacs-2021-patch/python_packaging/src
 pip install .
popd
