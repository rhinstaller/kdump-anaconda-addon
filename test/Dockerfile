FROM fedora:rawhide

RUN dnf update -y \
  && dnf install -y \
  make \
  anaconda \
  python3-pip \
  && dnf clean all

RUN pip install \
  pylint \
  pytest

RUN mkdir /kdump-anaconda-addon
WORKDIR /kdump-anaconda-addon
