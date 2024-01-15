FROM ubuntu:latest

SHELL ["/bin/bash", "-c"]
COPY install_deps.sh /
RUN bash install_deps.sh
COPY install_emsdk.sh /
RUN bash install_emsdk.sh
ENV PATH /emsdk:/emsdk/upstream/emscripten:/emsdk/node/16.20.0_64bit/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV EMSDK /emsdk
ENV EMSDK_NODE /emsdk/node/16.20.0_64bit/bin/node
CMD /bin/bash
