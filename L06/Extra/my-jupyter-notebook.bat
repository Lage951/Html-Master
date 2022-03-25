ECHO OFF

REM my-jupyter-notebook
REM  Version: 0.1
REM    2022-03-23: CEF, inital version

echo MY-JUPYTER-NOTEBOOK launcher..

@CALL "%HOMEPATH%\Anaconda3\condabin\conda.bat" activate swmal %* <NUL

REM notebooks start in this directory, you may change it..
cd \

REM then launch the notebook..
jupyter-notebook

echo DONE