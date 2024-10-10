# How you deploy streamlit app in VM
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
