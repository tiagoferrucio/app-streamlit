# How you deploy streamlit app in VM

Disclaimer

This repository and its contents are my own and do not represent any vendors' opinions, strategies, positions, or views. The code and any associated documentation made available in this repository are provided "as-is," without any warranties, including but not limited to fitness for a particular purpose.
I am not responsible for any support, updates, or fixes to the code and/or documentation present in this repository. Any use of this repository, including the code and related resources, is the sole responsibility of the user, and I do not assume any responsibility for damages or losses caused by the use of the content.

-----

- Run the commands below:
```python
sudo apt update
```
```python
sudo apt-get update
```
```python
sudo apt upgrade -y
```
```python
sudo apt install git curl unzip tar make sudo vim wget -y
```
```python
git clone "Your-repository"
```
```python
sudo apt install python3-pip
```
```python
pip3 install -r requirements.txt
```
```python
#Temporary running
python3 -m streamlit run app.py
```
```python
#Permanent running
nohup python3 -m streamlit run app.py
```
Note: Streamlit runs on this port: 8501
