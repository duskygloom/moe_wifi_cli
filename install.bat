@echo OFF

set pyexe=python
set appdir=%CD%
set runscript=moe.bat

echo Installing requirements...
%pyexe% -m pip install -r requirements.txt

echo:
copy sample_config.json config.json

echo:
echo Writing script...
echo @echo OFF> %runscript%
echo set prevdir=%%CD%%>> %runscript%
echo set appdir=%appdir%>> %runscript%
echo cd %%appdir%%
echo %pyexe% main.py %%*>> %runscript%
echo cd %%prevdir%%>> %runscript%

echo:
echo Done.
