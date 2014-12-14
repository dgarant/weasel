from OpenSSL import crypto, SSL
from socket import gethostname
from time import gmtime, mktime
from os.path import exists, join


class KeyManager:
    """ Manages the public and private key used by OpenSSL """

    CERT_FILE = "weasel.crt"
    KEY_FILE = "weasel.key"

    def __init__(self, keydir):
        self.keydir = keydir

    def get_cert_file(self):
        return join(self.keydir, self.CERT_FILE)

    def get_key_file(self):
        return join(self.keydir, self.KEY_FILE)

    def create_keys(self):
        """
        If either the key or certificate do not exist in the specified directory,
        create them in that directory.
        """

        if not exists(join(self.keydir, self.CERT_FILE)) \
                or not exists(join(self.keydir, self.KEY_FILE)):
                
            # create a key pair
            k = crypto.PKey()
            k.generate_key(crypto.TYPE_RSA, 1024)

            # create a self-signed cert
            cert = crypto.X509()
            cert.get_subject().C = "US"
            cert.get_subject().ST = "Minnesota"
            cert.get_subject().L = "Minnetonka"
            cert.get_subject().O = "my company"
            cert.get_subject().OU = "my organization"
            cert.get_subject().CN = gethostname()
            cert.set_serial_number(1000)
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(10*365*24*60*60)
            cert.set_issuer(cert.get_subject())
            cert.set_pubkey(k)
            cert.sign(k, 'sha1')

            open(join(self.keydir, self.CERT_FILE), "wt").write(
                crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
            open(join(self.keydir, self.KEY_FILE), "wt").write(
                crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
