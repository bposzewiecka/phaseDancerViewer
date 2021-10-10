# PhaseDancerViewer

##  Installation

### Step 1: Installing django application

To install PhaseDancerViewer djnago application you have to execute the following commands:

```
python3 -m venv phaseDancerViewer_venv
source phaseDancerViewer_venv/bin/activate
git clone https://github.com/bposzewiecka/phaseDancerViewer.git
cd  phaseDancerViewer
pip install -r requirements.txt
```

### Step 2: Creating symbolic link to phaseDancer directory

Assummed you have **phaseDancer** installed in *path_to_dir/phaseDancer* directory, following command:

```
cd static
ln -s phaseDancer path_to_dir/phaseDancer
```

will create symbolic link that connect **phaseDancer** assembler results with the **PhaseDancerViewer** application.

### Step 3: 

Click on the button "Load configuration file" to load metadata of sample and created contigs.
This step may be repeated if configuration file will change.
