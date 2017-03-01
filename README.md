# Baker Store Front

This is a store front for a baker written in google app engine, and using google checkout.
It provides a product slideshow, and featured product list, and the ability to purchase goods.
An admin page alows the creation of new products, the ability to upload image files, and change the 
merchant id.

## Run in development mode
```bash
dev_appserver.py app.yaml 
```

## Dependencies
In order to run you need google app engin with the python module and the datastore module. Below are the commands needed for Ubuntu 16.04
```bash
export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)"
echo "deb https://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update && sudo apt-get install google-cloud-sdk google-cloud-sdk-app-engine-python google-cloud-sdk-datastore-emulator
gcloud auth login
cd BakeryStoreFront/src
dev_appserver.py app.yaml
```