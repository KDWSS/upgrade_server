# PUSH-based SW update mechanism

This project introduces functionality to manage system upgrades for embedded devices with different upgrade approaches.
In order to support this feature the separate lightweight HTTP server is run on every embedded device and hides the local upgrade system.

At the moment this service is able to communication with the SW update and RAUC.

Server provides API to allow communication with it. 

## Getting Started
### RAUC part
Prepare the yocto build with RAUC support:
This instruction is based on the [Getting Started with RAUC on Raspberry Pi ](https://www.konsulko.com/getting-started-with-rauc-on-raspberry-pi-2/)

```
	git clone -b dunfell git://git.yoctoproject.org/poky poky-rpi-rauc
	git clone -b dunfell git://git.openembedded.org/meta-openembedded
	git clone -b dunfell git://git.yoctoproject.org/meta-raspberrypi
	git clone -b dunfell https://github.com/rauc/meta-rauc.git
	git clone -b dunfell https://github.com/leon-anavi/meta-rauc-community.git
	
	git clone -b master  https://github.com/mera-company/meta-upgrade-server
	
	source oe-init-build-env
```
Add particular layers

```
	bitbake-layers add-layer ../meta-openembedded/meta-oe/
	bitbake-layers add-layer ../meta-openembedded/meta-python/
	bitbake-layers add-layer ../meta-openembedded/meta-networking/
	bitbake-layers add-layer ../meta-openembedded/meta-multimedia/
	bitbake-layers add-layer ../meta-raspberrypi/
	bitbake-layers add-layer ../meta-rauc
	bitbake-layers add-layer ../meta-rauc-community/meta-rauc-raspberrypi/
```
Add layer for the layer for upgrade service

```
	bitbake-layers add-layer ../meta-upgrade-server

```

Correct conf/local.conf 

```
MACHINE = "raspberrypi4"

DISTRO_FEATURES_append = " systemd"
VIRTUAL-RUNTIME_init_manager = "systemd"
DISTRO_FEATURES_BACKFILL_CONSIDERED = "sysvinit"
VIRTUAL-RUNTIME_initscripts = ""

IMAGE_INSTALL_append = " rauc"

IMAGE_FSTYPES="tar.bz2 ext4 wic.bz2 wic.bmap"
SDIMG_ROOTFS_TYPE="ext4"
ENABLE_UART = "1"
RPI_USE_U_BOOT = "1"
PREFERRED_PROVIDER_virtual/bootloader = "u-boot"

WKS_FILE = "sdimage-dual-raspberrypi.wks"

IMAGE_INSTALL_append = " update-scripts"
```
Build the bundle
At first the the initial image could eb prepared
```bitbake core-image-minimal```

After that the changes in the build could be added (new applications etc) and the bundle for the upgrade could be prepared
```bitbake update-bundle```

### SW update part

Prepare the yocto build

mkdir yocto && cd yocto

```
mkdir layers && cd layers
git clone git://git.yoctoproject.org/poky -b zeus
git clone git://github.com/openembedded/meta-openembedded.git -b zeus
git clone https://github.com/agherzan/meta-raspberrypi.git -b zeus
git clone https://github.com/sbabic/meta-swupdate -b zeus

```

Add the special repositories for raspberry pi

```
git clone -b master https://github.com/mera-company/meta-swupdate-rpi
git clone -b master https://github.com/mera-company/meta-upgrade-server
source oe-init-build-env
```
Add the particular layers

```
bitbake-layers add-layer ../layers/meta-openembedded/meta-oe
bitbake-layers add-layer ../layers/meta-openembedded/meta-python
bitbake-layers add-layer ../layers/meta-openembedded/meta-networking
bitbake-layers add-layer ../layers/meta-openembedded/meta-multimedia
bitbake-layers add-layer ../layers/meta-raspberrypi
bitbake-layers add-layer ../layers/meta-swupdate
```

Add the special layers for upgrade server

```
bitbake-layers add-layer ../layers/meta-swupdate-rpi
bitbake-layers add-layer ../meta-upgrade-server
```
Add the following lines in conf.local

```
MACHINE = "raspberrypi3"

RPI_USE_U_BOOT = "1"
IMAGE_FSTYPES = " rpi-sdimg ext4.gz"

DISTRO_FEATURES_append = " systemd"
VIRTUAL-RUNTIME_init_manager = "systemd"

IMAGE_ROOTFS_EXTRA_SPACE = "1000000"

IMAGE_INSTALL_append = " update-scripts"
IMAGE_INSTALL_append = " bzip2 tree nano"

```

and build the image 

```
bitbake update-image
```

## Prerequisites

## Installing

## Built With
* [RAUC](https://rauc.io) - Update client for embedded linux
* [SW Update](https://sbabic.github.io/swupdate/) - Update client for embedded linux
* [Flask](https://flask.palletsprojects.com) - lightweight WSGI web application framework
* [Raspberry Pi](https://www.raspberrypi.org) - Raspberry Pi 4 adapted kernel and firmware
* [DBus](https://www.freedesktop.org/wiki/Software/dbus/)

## Limitations
* The systems with RAUC update are supported only on the raspberry PI4. Yocto release: dunfell
* The systems with SW update are supported only on the raspbery PI3; Yocto release: zeus

* The service uses the binary update packages specific for the particular update system (RAUC/SW update).
  It is up to user to use correct update package depending on the system properties. Note that update system type for the particular device could be get through the API.

## Versioning

We use [SemVer](http://semver.org/) for versioning. 

## Authors

Leonid Lazarev <leonid.lazarev@orioninc.com>

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the MIT license. See the [COPYING.MIT](COPYING.MIT) file for details.
