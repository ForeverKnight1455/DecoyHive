FROM ubuntu:20.04
LABEL maintainer="SystemClone"

# Set non-interactive mode (for Debian-based systems)
ENV DEBIAN_FRONTEND=noninteractive

# Update system packages
RUN apt-get update

RUN useradd -m -d /home/sreyas -s /bin/bash sreyas
ENV SHELL="/bin/bash"
ENV WSL2_GUI_APPS_ENABLED="1"
ENV WSL_DISTRO_NAME="kali-linux"
ENV WT_SESSION="c7a39d0d-ffdb-4337-b960-042201b06631"
ENV LESS_TERMCAP_se="[0m"
ENV LESS_TERMCAP_so="[01;33m"
ENV NAME="DESKTOP-C04SPAD"
ENV PWD="/mnt/c/code/github/DecoyHive"
ENV LOGNAME="sreyas"
ENV QT_QPA_PLATFORMTHEME="qt5ct"
ENV XAUTHORITY="/home/sreyas/.Xauthority"
ENV HOME="/home/sreyas"
ENV LANG="en_US.UTF-8"
ENV WSL_INTEROP="/run/WSL/44_interop"
ENV LS_COLORS="rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=00:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.7z=01;31:*.ace=01;31:*.alz=01;31:*.apk=01;31:*.arc=01;31:*.arj=01;31:*.bz=01;31:*.bz2=01;31:*.cab=01;31:*.cpio=01;31:*.crate=01;31:*.deb=01;31:*.drpm=01;31:*.dwm=01;31:*.dz=01;31:*.ear=01;31:*.egg=01;31:*.esd=01;31:*.gz=01;31:*.jar=01;31:*.lha=01;31:*.lrz=01;31:*.lz=01;31:*.lz4=01;31:*.lzh=01;31:*.lzma=01;31:*.lzo=01;31:*.pyz=01;31:*.rar=01;31:*.rpm=01;31:*.rz=01;31:*.sar=01;31:*.swm=01;31:*.t7z=01;31:*.tar=01;31:*.taz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tgz=01;31:*.tlz=01;31:*.txz=01;31:*.tz=01;31:*.tzo=01;31:*.tzst=01;31:*.udeb=01;31:*.war=01;31:*.whl=01;31:*.wim=01;31:*.xz=01;31:*.z=01;31:*.zip=01;31:*.zoo=01;31:*.zst=01;31:*.avif=01;35:*.jpg=01;35:*.jpeg=01;35:*.mjpg=01;35:*.mjpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.webp=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.m4a=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:*~=00;90:*#=00;90:*.bak=00;90:*.crdownload=00;90:*.dpkg-dist=00;90:*.dpkg-new=00;90:*.dpkg-old=00;90:*.dpkg-tmp=00;90:*.old=00;90:*.orig=00;90:*.part=00;90:*.rej=00;90:*.rpmnew=00;90:*.rpmorig=00;90:*.rpmsave=00;90:*.swp=00;90:*.tmp=00;90:*.ucf-dist=00;90:*.ucf-new=00;90:*.ucf-old=00;90::ow=30;44:"
ENV WAYLAND_DISPLAY="wayland-0"
ENV TERM="xterm-256color"
ENV LESS_TERMCAP_mb="[1;31m"
ENV LESS_TERMCAP_me="[0m"
ENV LESS_TERMCAP_md="[1;36m"
ENV USER="sreyas"
ENV DISPLAY=":0"
ENV LESS_TERMCAP_ue="[0m"
ENV SHLVL="1"
ENV LESS_TERMCAP_us="[1;32m"
ENV XDG_RUNTIME_DIR="/mnt/wslg/runtime-dir"
ENV WSLENV="WT_SESSION:WT_PROFILE_ID:"
ENV QT_AUTO_SCREEN_SCALE_FACTOR="0"
ENV PATH="/home/sreyas/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib:/mnt/c/app/Sreyas/product/21c/dbhomeXE/bin:/mnt/c/Program Files/Common Files/Oracle/Java/javapath:/mnt/c/Windows/system32:/mnt/c/Windows:/mnt/c/Windows/System32/Wbem:/mnt/c/Windows/System32/WindowsPowerShell/v1.0/:/mnt/c/Windows/System32/OpenSSH/:/mnt/c/Program Files (x86)/NVIDIA Corporation/PhysX/Common:/mnt/c/Program Files (x86)/dotnet/:/mnt/c/Program Files/dotnet/:/mnt/c/MinGW/bin:/mnt/c/Program Files/Java/jdk-21/bin:/mnt/c/Program Files/MySQL/MySQL Server 8.0/bin:/mnt/c/Program Files/Git/cmd:/mnt/c/Program Files/nodejs/:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/Programs/Python/Python312:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/Programs/Python/Python312/Scripts:/mnt/c/Program Files/NVIDIA Corporation/NVIDIA app/NvDLISR:/mnt/c/metasploit-framework/bin/:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/flutter/bin:/mnt/c/Program Files/WireGuard/:/mnt/c/Program Files/Cloudflare/Cloudflare WARP/:/mnt/c/Program Files/Docker/Docker/resources/bin:/mnt/c/Program Files/MySQL/MySQL Shell 8.0/bin/:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/Programs/Python/Python311/Scripts/:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/Programs/Python/Python311/:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/Programs/Python/Launcher/:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/Microsoft/WindowsApps:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/Programs/Microsoft VS Code/bin:/mnt/c/Users/Sreyas P Pradeep/AppData/Roaming/npm:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/GitHubDesktop/bin:/mnt/c/Program Files (x86)/Nmap:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/flutter/bin:/mnt/c/Users/Sreyas P Pradeep/AppData/Local/Programs/cursor/resources/app/bin"
ENV HOSTTYPE="x86_64"
ENV PULSE_SERVER="unix:/mnt/wslg/PulseServer"
ENV WT_PROFILE_ID="{9963591c-3977-4599-8cd1-b0b7efb72484}"
ENV _="/usr/bin/python"
ENV OLDPWD="/home/sreyas"

# Configure networking
RUN echo "IP Address: 172.19.161.99 10.10.15.159 dead:beef:2::119d"
# Configure firewall rules

CMD ["tail", "-f", "/dev/null"]