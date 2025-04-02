
Vagrant.configure("2") do |config|
    config.vm.box = "archlinux/archlinux"

    # Shared network with the host
    config.vm.network "public_network", bridge: "enp0s3", use_dhcp_assigned_default_route: true

    config.vm.provider "virtualbox" do |vb|
        vb.customize ["modifyvm", :id, "--cpus", 2]
        vb.customize ["modifyvm", :id, "--memory", 1024]
    end

    config.vm.provider "libvirt" do |lv|
        lv.cpus = 2
        lv.memory = 1024
        lv.networks << { network_name: "default", type: "bridge" }
        lv.qemuargs = [
            ["-smbios", "type=1,manufacturer=SpoofedVendor,product=SpoofedModel,serial=12345678"],
            ["-smbios", "type=17,size=13916"],
            ["-smbios", "type=4,core=4"]
        ]
    end
end
