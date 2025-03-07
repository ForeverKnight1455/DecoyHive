FROM ubuntu:20.04
LABEL maintainer="DecoyHive"

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update and install packages
RUN apt-get update && apt-get install -y \
    net-tools \
    iptables \
    iproute2 && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -d /usr/lib/dhcpcd -s /bin/false dhcpcd
RUN useradd -m -d /nonexistent -s /usr/sbin/nologin tcpdump
RUN useradd -m -d /run/sshd -s /usr/sbin/nologin sshd
RUN useradd -m -d /home/sreyas -s /bin/bash sreyas
RUN useradd -m -d /var/lib/tpm -s /bin/false tss
RUN useradd -m -d /var/lib/strongswan -s /usr/sbin/nologin strongswan
RUN useradd -m -d /run/xrdp -s /usr/sbin/nologin xrdp
RUN useradd -m -d /var/lib/misc -s /usr/sbin/nologin dnsmasq
RUN useradd -m -d /run/avahi-daemon -s /usr/sbin/nologin avahi
RUN useradd -m -d /var/lib/openvpn/chroot -s /usr/sbin/nologin nm-openvpn
RUN useradd -m -d /run/speech-dispatcher -s /bin/false speech-dispatcher
RUN useradd -m -d /var/lib/usbmux -s /usr/sbin/nologin usbmux
RUN useradd -m -d /var/lib/NetworkManager -s /usr/sbin/nologin nm-openconnect
RUN useradd -m -d /run/pulse -s /usr/sbin/nologin pulse
RUN useradd -m -d /var/lib/lightdm -s /bin/false lightdm
RUN useradd -m -d /var/lib/saned -s /usr/sbin/nologin saned
RUN useradd -m -d / -s /usr/sbin/nologin polkitd
RUN useradd -m -d /proc -s /usr/sbin/nologin rtkit
RUN useradd -m -d /var/lib/colord -s /usr/sbin/nologin colord
RUN useradd -m -d /var/log/snort -s /usr/sbin/nologin snort

# Set environment variables
ENV SHELL="/bin/bash"
ENV SESSION_MANAGER="local/DESKTOP-C04SPAD:@/tmp/.ICE-unix/430,unix/DESKTOP-C04SPAD:/tmp/.ICE-unix/430"
ENV WINDOWID="0"
ENV COLORTERM="truecolor"
ENV XDG_CONFIG_DIRS="/etc/xdg"
ENV XDG_MENU_PREFIX="xfce-"
ENV WSL2_GUI_APPS_ENABLED="1"
ENV WSL_DISTRO_NAME="kali-linux"
ENV WT_SESSION="37c12576-8b50-4188-a4d0-faade120b5ac"
ENV LANGUAGE=""
ENV LESS_TERMCAP_se="[0m"
ENV LESS_TERMCAP_so="[01;33m"
ENV XDG_CONFIG_HOME="/home/sreyas/.config"
ENV DESKTOP_SESSION="xfce"
ENV SSH_AGENT_PID="475"
ENV NAME="DESKTOP-C04SPAD"
ENV PWD="/mnt/c/code/github/DecoyHive"
ENV LOGNAME="sreyas"
ENV QT_QPA_PLATFORMTHEME="qt5ct"
ENV XDG_SESSION_TYPE="x11"
ENV XAUTHORITY="/home/sreyas/.Xauthority"
ENV HOME="/home/sreyas"
ENV LANG="en_US.UTF-8"
ENV WSL_INTEROP="/run/WSL/10_interop"
ENV LS_COLORS="rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=00:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.7z=01;31:*.ace=01;31:*.alz=01;31:*.apk=01;31:*.arc=01;31:*.arj=01;31:*.bz=01;31:*.bz2=01;31:*.cab=01;31:*.cpio=01;31:*.crate=01;31:*.deb=01;31:*.drpm=01;31:*.dwm=01;31:*.dz=01;31:*.ear=01;31:*.egg=01;31:*.esd=01;31:*.gz=01;31:*.jar=01;31:*.lha=01;31:*.lrz=01;31:*.lz=01;31:*.lz4=01;31:*.lzh=01;31:*.lzma=01;31:*.lzo=01;31:*.pyz=01;31:*.rar=01;31:*.rpm=01;31:*.rz=01;31:*.sar=01;31:*.swm=01;31:*.t7z=01;31:*.tar=01;31:*.taz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tgz=01;31:*.tlz=01;31:*.txz=01;31:*.tz=01;31:*.tzo=01;31:*.tzst=01;31:*.udeb=01;31:*.war=01;31:*.whl=01;31:*.wim=01;31:*.xz=01;31:*.z=01;31:*.zip=01;31:*.zoo=01;31:*.zst=01;31:*.avif=01;35:*.jpg=01;35:*.jpeg=01;35:*.mjpg=01;35:*.mjpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.webp=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.m4a=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:*~=00;90:*#=00;90:*.bak=00;90:*.crdownload=00;90:*.dpkg-dist=00;90:*.dpkg-new=00;90:*.dpkg-old=00;90:*.dpkg-tmp=00;90:*.old=00;90:*.orig=00;90:*.part=00;90:*.rej=00;90:*.rpmnew=00;90:*.rpmorig=00;90:*.rpmsave=00;90:*.swp=00;90:*.tmp=00;90:*.ucf-dist=00;90:*.ucf-new=00;90:*.ucf-old=00;90::ow=30;44:"
ENV XDG_CURRENT_DESKTOP="XFCE"
ENV VNCDESKTOP="DESKTOP-C04SPAD.:1 (sreyas)"
ENV WAYLAND_DISPLAY="wayland-0"
ENV XDG_CACHE_HOME="/home/sreyas/.cache"
ENV XDG_SESSION_CLASS="user"
ENV TERM="xterm-256color"
ENV LESS_TERMCAP_mb="[1;31m"
ENV LESS_TERMCAP_me="[0m"
ENV LESS_TERMCAP_md="[1;36m"
ENV USER="sreyas"
ENV COLORFGBG="15;0"
ENV DISPLAY=":1.0"
ENV SHLVL="3"
ENV LESS_TERMCAP_ue="[0m"
ENV LESS_TERMCAP_us="[1;32m"
ENV XDG_RUNTIME_DIR="/mnt/wslg/runtime-dir"
ENV WSLENV="WT_SESSION:WT_PROFILE_ID:"
ENV QT_AUTO_SCREEN_SCALE_FACTOR="0"
ENV XDG_DATA_DIRS="/usr/local/share:/usr/share"
ENV GDK_BACKEND="x11"
ENV PATH="/home/sreyas/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib:/mnt/c/app/Sreyas/product/21c/dbhomeXE/bin:/mnt/c/Program Files/Common Files/Oracle/Java/javapath:/mnt/c/Windows/system32:/mnt/c/Windows:/mnt/c/Windows/System32/Wbem:/mnt/c/Windows/System32/WindowsPowerShell/v1.0/:/mnt/c/Windows/System32/OpenSSH/:/mnt/c/Program Files (x86)/NVIDIA Corporation/PhysX/Common:/mnt/c/Program Files (x86)/dotnet/:/mnt/c/Program Files/dotnet/:/mnt/c/MinGW/bin:/mnt/c/Program Files/Java/jdk-21/bin:/mnt/c/Program Files/MySQL/MySQL Server 8.0/bin:/mnt/c/Program Files/Git/cmd:/mnt/c/Program Files/nodejs/:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/Programs/Python/Python312:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/Programs/Python/Python312/Scripts:/mnt/c/Program Files/NVIDIA Corporation/NVIDIA app/NvDLISR:/mnt/c/metasploit-framework/bin/:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/flutter/bin:/mnt/c/Program Files/WireGuard/:/mnt/c/Program Files/Cloudflare/Cloudflare WARP/:/mnt/c/Program Files/Docker/Docker/resources/bin:/mnt/c/Program Files/MySQL/MySQL Shell 8.0/bin/:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/Programs/Python/Python311/Scripts/:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/Programs/Python/Python311/:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/Programs/Python/Launcher/:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/Microsoft/WindowsApps:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/Programs/Microsoft VS Code/bin:/mnt/c/Users/Sreyas P Pradeep/AppData/Roaming/npm:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/GitHubDesktop/bin:/mnt/c/Program Files (x86)/Nmap:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/flutter/bin"
ENV DBUS_SESSION_BUS_ADDRESS="unix:path=/tmp/dbus-W3M0mcNLKx,guid=22d296cda212dd164908e20e67c9d9a5"
ENV HOSTTYPE="x86_64"
ENV PULSE_SERVER="tcp:176.20.0.74"
ENV WT_PROFILE_ID="{9963591c-3977-4599-8cd1-b0b7efb72484}"
ENV OLDPWD="/mnt/c/code/github"
ENV _="/usr/bin/python3"

# Keep container running
CMD ["tail", "-f", "/dev/null"]