
from support import logger, from_json, validate_json_schema;
import os;
import sys;
import jinja2;

class configure_dns_servers:
    def __init__(self):
        self.dns_servers = from_json("config/dns-servers.json");
        self.download_and_install_dns_software();

    def download_and_install_dns_software(self):
        logger.info("Update the system repositories and install the DNS software.");
        os.system("sudo apt update");
        os.system("sudo apt install bind9 bind9utils bind9-doc -y");
        self.prepare_and_replace_dns_configuration();

    def prepare_and_replace_dns_configuration(self):
        logger.info("Prepare and replace the DNS configuration file \"/etc/default/named\".");
        self.render_and_replace_system_files("template/named", "/etc/default/named");
        self.restart_dns_service();
        self.prepare_and_replace_dns_configuration_options();

    def prepare_and_replace_dns_configuration_options(self):
        logger.info("Prepare and replace the DNS configuration file \"/etc/bind/named.conf.options\".");
        self.render_and_replace_system_files("template/named.conf.options", "/etc/bind/named.conf.options", dns_servers=self.dns_servers);
        self.restart_dns_service();

    def render_and_replace_system_files(self, template, path, **kargs):
        if os.path.exists(template):
            with open(template, "r") as file:
                template = jinja2.Template(file.read());
            if os.path.exists(path):
                os.system(f"cp {path} {path}_$(date +'%Y%m%d_%H%M%S')");
            with open(path, "w") as file:
                file.write(template.render(**kargs));
        else:
            logger.critical("The template doesn't exist for the DNS configuration file \"{path}\".");
            sys.exit(1);

    def restart_dns_service(self):
        logger.info("Restart the DNS service and validate.");
        os.system("sudo systemctl restart bind9");

def main():
    validate_json_schema("config/dns-servers.json", "schema/dns-servers-schema.json");
    configure_dns_servers();

if "__main__" in __name__:
    if os.geteuid() != 0:
        logger.critical("Please execute a script with root privileges.");
    else:
        if os.path.isfile("requirements.txt"):
            logger.info("Download the required libraries and install them on the system.");
            os.system("pip install -r requirements.txt");
        main();