import json
import sys

def generate_vagrantfile(config_json):

    box_name_map = {
        "arch": "archlinux/archlinux",
        "ubuntu": "ubuntu/focal64",
        "debian": "debian/bullseye64",
        "centos": "centos/7",
        "fedora": "fedora/34-cloud-base",
        "opensuse": "opensuse/openSUSE-42.3-x86_64",
        "alpine": "alpine/alpine64",
        "gentoo": "gentoo/gentoo",
        "oracle": "oraclelinux/7",
        "freebsd": "freebsd/FreeBSD-12.1-RELEASE"
    }

    config = json.loads(config_json)
    os_type = config["os"].get("detected_distro", "generic").lower()
    box_name = box_name_map.get(os_type, "generic/ubuntu")  # Fallback

    spoofed_cpu_cores = config["hardware"]["cpu"].get("cores", 4)
    spoofed_memory_gb = float(config["hardware"]["memory"].get("total", "4.0 GB").split()[0])

    actual_cpu_cores = min(2, spoofed_cpu_cores)
    actual_memory_mb = min(1024, int(spoofed_memory_gb * 1024))  # Max 1GB allocation

    vagrantfile_content = f'''
Vagrant.configure("2") do |config|
    config.vm.box = "{box_name}"

    # Shared network with the host
    config.vm.network "private_network", type: "dhcp"
    config.vm.provider "virtualbox" do |vb|
        vb.customize ["modifyvm", :id, "--cpus", {actual_cpu_cores}]
        vb.customize ["modifyvm", :id, "--memory", {actual_memory_mb}]
    end

    config.vm.provider "libvirt" do |lv|
        lv.cpus = {actual_cpu_cores}
        lv.memory = {actual_memory_mb}
        lv.networks << {{ network_name: "default", type: "bridge" }}
        lv.qemuargs = [
            ["-smbios", "type=1,manufacturer=SpoofedVendor,product=SpoofedModel,serial=12345678"],
            ["-smbios", "type=17,size={int(spoofed_memory_gb * 1024)}"],
            ["-smbios", "type=4,core={spoofed_cpu_cores}"]
        ]
    end
end
'''

    return vagrantfile_content

if __name__ == "__main__":
    print("""Provide path to the configuration file eg. python3 vagrant_gen.py /path/to/config.json""")
    config_file_path = sys.argv[1]
    print(config_file_path)

    with open(config_file_path, 'r') as file:
        config_json = file.read()

    contents = generate_vagrantfile(config_json)
    with open("Vagrantfile", "w") as file:
        file.write(contents)
    print("Vagrantfile generated successfully!")
