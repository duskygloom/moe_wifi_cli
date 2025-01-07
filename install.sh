#!/usr/bin/env bash

pybin=python3
appdir=`pwd`

echo "Installing requirements..."
$pybin -m pip install -r requirements.txt

cp sample_config.json config.json

echo -e "\nWriting script..."
echo "#!/usr/bin/env bash
prevdir=\`pwd\`
cd $appdir
$pybin main.py \$@
cd \$prevdir" > ./moe

chmod +x ./moe
echo -e "\nDone."
