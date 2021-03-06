# PhaseDancerViewer

##  Installation

### Step 1: Installing django PhaseDancerViewer application

To install PhaseDancerViewer django application you have to execute the following commands:

```
python3 -m venv phaseDancerViewer_venv
source phaseDancerViewer_venv/bin/activate
git clone https://github.com/bposzewiecka/phaseDancerViewer.git
cd  phaseDancerViewer
pip install -r requirements.txt
python manage.py migrate
python manage.py shell < create_db_objects.py
```

### Step 2: Creating symbolic link to PhaseDancer assembler results

Assume you have **PhaseDancer** installed in *path_to_dir/phaseDancer* directory, following command:

```
ln -s static/phaseDancer path_to_dir/phaseDancer
```

will create symbolic link that connects **PhaseDancer** assembler results with the **PhaseDancerViewer** application.

### Step 3: Loading the configuration file

Click on the button "Load the configuration file" to load the metadata of samples and created contigs.
This step may be repeated if the configuration file will change.


## Screenshot of PhaseDancerViewer

![Image PhaseDancerViewer application](/phaseDancerViewer.png?raw=true "PhaseDancerViewer application")
