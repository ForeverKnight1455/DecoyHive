FROM archlinux:latest
LABEL maintainer="SystemClone"

# Set non-interactive mode
ENV DEBIAN_FRONTEND=noninteractive
RUN pacman -Sy

RUN useradd -m -d / -s /usr/bin/nologin nobody
RUN useradd -m -d /home/onegrit -s /bin/bash onegrit
RUN useradd -m -d /home/sambauser -s /sbin/nologin sambauser
ENV COLORTERM="truecolor"
ENV LANGUAGE=""
ENV LC_ADDRESS="en_IN"
ENV LC_NAME="en_IN"
ENV LC_MONETARY="en_IN"
ENV XAUTHORITY="/run/user/1000/xauth_VqCZIX"
ENV LC_PAPER="en_IN"
ENV LANG="en_US.UTF-8"
ENV LS_COLORS="rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=00:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.7z=01;31:*.ace=01;31:*.alz=01;31:*.apk=01;31:*.arc=01;31:*.arj=01;31:*.bz=01;31:*.bz2=01;31:*.cab=01;31:*.cpio=01;31:*.crate=01;31:*.deb=01;31:*.drpm=01;31:*.dwm=01;31:*.dz=01;31:*.ear=01;31:*.egg=01;31:*.esd=01;31:*.gz=01;31:*.jar=01;31:*.lha=01;31:*.lrz=01;31:*.lz=01;31:*.lz4=01;31:*.lzh=01;31:*.lzma=01;31:*.lzo=01;31:*.pyz=01;31:*.rar=01;31:*.rpm=01;31:*.rz=01;31:*.sar=01;31:*.swm=01;31:*.t7z=01;31:*.tar=01;31:*.taz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tgz=01;31:*.tlz=01;31:*.txz=01;31:*.tz=01;31:*.tzo=01;31:*.tzst=01;31:*.udeb=01;31:*.war=01;31:*.whl=01;31:*.wim=01;31:*.xz=01;31:*.z=01;31:*.zip=01;31:*.zoo=01;31:*.zst=01;31:*.avif=01;35:*.jpg=01;35:*.jpeg=01;35:*.mjpg=01;35:*.mjpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.webp=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.m4a=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:*~=00;90:*#=00;90:*.bak=00;90:*.crdownload=00;90:*.dpkg-dist=00;90:*.dpkg-new=00;90:*.dpkg-old=00;90:*.dpkg-tmp=00;90:*.old=00;90:*.orig=00;90:*.part=00;90:*.rej=00;90:*.rpmnew=00;90:*.rpmorig=00;90:*.rpmsave=00;90:*.swp=00;90:*.tmp=00;90:*.ucf-dist=00;90:*.ucf-new=00;90:*.ucf-old=00;90:"
ENV XDG_CURRENT_DESKTOP="KDE"
ENV TERM="xterm-256color"
ENV LC_IDENTIFICATION="en_IN"
ENV DISPLAY=":1"
ENV LC_TELEPHONE="en_IN"
ENV LC_MEASUREMENT="en_IN"
ENV PS1="(venv) [/u@/h /W]/$ "
ENV LC_TIME="en_IN"
ENV PATH="/usr/local/sbin:/usr/local/bin:/usr/bin"
ENV LC_NUMERIC="en_IN"
ENV MAIL="/var/mail/root"
ENV LOGNAME="root"
ENV USER="root"
ENV HOME="/root"
ENV SHELL="/usr/bin/bash"
ENV SUDO_COMMAND="/usr/bin/python3 analyzer"
ENV SUDO_USER="onegrit"
ENV SUDO_UID="1000"
ENV SUDO_GID="1000"
ENV SUDO_HOME="/home/onegrit"
ENV BROWSER="firefox"
ENV EDITOR="nano"

# Configure networking
RUN echo "IP Address: "
# Configure firewall rules
RUN iptables Chain INPUT (policy ACCEPT)
RUN iptables target     prot opt source               destination         
RUN iptables Chain FORWARD (policy DROP)
RUN iptables target     prot opt source               destination         
RUN iptables DOCKER-USER  all  --  anywhere             anywhere            
RUN iptables DOCKER-ISOLATION-STAGE-1  all  --  anywhere             anywhere            
RUN iptables ACCEPT     all  --  anywhere             anywhere             ctstate RELATED,ESTABLISHED
RUN iptables DOCKER     all  --  anywhere             anywhere            
RUN iptables ACCEPT     all  --  anywhere             anywhere            
RUN iptables ACCEPT     all  --  anywhere             anywhere            
RUN iptables ACCEPT     all  --  anywhere             anywhere             ctstate RELATED,ESTABLISHED
RUN iptables DOCKER     all  --  anywhere             anywhere            
RUN iptables ACCEPT     all  --  anywhere             anywhere            
RUN iptables ACCEPT     all  --  anywhere             anywhere            
RUN iptables ACCEPT     all  --  anywhere             anywhere             ctstate RELATED,ESTABLISHED
RUN iptables DOCKER     all  --  anywhere             anywhere            
RUN iptables ACCEPT     all  --  anywhere             anywhere            
RUN iptables ACCEPT     all  --  anywhere             anywhere            
RUN iptables ACCEPT     all  --  anywhere             anywhere             ctstate RELATED,ESTABLISHED
RUN iptables DOCKER     all  --  anywhere             anywhere            
RUN iptables ACCEPT     all  --  anywhere             anywhere            
RUN iptables ACCEPT     all  --  anywhere             anywhere            
RUN iptables ACCEPT     all  --  anywhere             anywhere             ctstate RELATED,ESTABLISHED
RUN iptables DOCKER     all  --  anywhere             anywhere            
RUN iptables ACCEPT     all  --  anywhere             anywhere            
RUN iptables ACCEPT     all  --  anywhere             anywhere            
RUN iptables Chain OUTPUT (policy ACCEPT)
RUN iptables target     prot opt source               destination         
RUN iptables Chain DOCKER (5 references)
RUN iptables target     prot opt source               destination         
RUN iptables Chain DOCKER-ISOLATION-STAGE-1 (1 references)
RUN iptables target     prot opt source               destination         
RUN iptables DOCKER-ISOLATION-STAGE-2  all  --  anywhere             anywhere            
RUN iptables DOCKER-ISOLATION-STAGE-2  all  --  anywhere             anywhere            
RUN iptables DOCKER-ISOLATION-STAGE-2  all  --  anywhere             anywhere            
RUN iptables DOCKER-ISOLATION-STAGE-2  all  --  anywhere             anywhere            
RUN iptables DOCKER-ISOLATION-STAGE-2  all  --  anywhere             anywhere            
RUN iptables RETURN     all  --  anywhere             anywhere            
RUN iptables Chain DOCKER-ISOLATION-STAGE-2 (5 references)
RUN iptables target     prot opt source               destination         
RUN iptables DROP       all  --  anywhere             anywhere            
RUN iptables DROP       all  --  anywhere             anywhere            
RUN iptables DROP       all  --  anywhere             anywhere            
RUN iptables DROP       all  --  anywhere             anywhere            
RUN iptables DROP       all  --  anywhere             anywhere            
RUN iptables RETURN     all  --  anywhere             anywhere            
RUN iptables Chain DOCKER-USER (1 references)
RUN iptables target     prot opt source               destination         
RUN iptables RETURN     all  --  anywhere             anywhere

# Enable system services
RUN systemctl enable nginx || true
RUN systemctl enable com.docker.backend || true
RUN systemctl enable kdeconnectd || true

CMD ["tail", "-f", "/dev/null"]