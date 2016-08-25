# Main Application

#
# INCLUDES
#

# Local network functions
import libs.network
# Required for complex command line argument parsing.
import argparse
# Required for configuration files
import ConfigParser
# Required for CSV
import csv
# Required for STDOUT
import sys

# MODULES:  Add additional intelligence source modules here

# Local GeoIP functions
import libs.geoip
# Local DNS functions
import libs.dnsinfo
# Local VirusTotal functions
import libs.vt
# Local PassiveTotal functions
import libs.pt

#
# COMMAND LINE ARGS
#

# Setup command line argument parsing.
parser = argparse.ArgumentParser(
    description='Modular application to look up host intelligence information. Outputs CSV to STDOUT. This application will not output information until it has finished all of the input.')
parser.add_argument('ConfigurationFile', help='Configuration file')
parser.add_argument('InputFile',
                    help='Input file, one host per line (IP, domain, or FQDN host name)')
parser.add_argument('-a','--all', action='store_true', help='Perform All Lookups.')
parser.add_argument('-d','--dns',  action='store_true', help='DNS Lookup.')
parser.add_argument('-v','--virustotal', action='store_true', help='VirusTotal Lookup.')
parser.add_argument('-p','--passivetotal', action='store_true', help='PassiveTotal Lookup.')
parser.add_argument('-s','--shodan', action='store_true', help='Shodan Lookup. (WORK IN PROGRESS)')
parser.add_argument('-c','--censys', action='store_true', help='Censys Lookup. (WORK IN PROGRESS)')
parser.add_argument('-t','--threatcrowd', action='store_true', help='ThreatCrowd Lookup. (WORK IN PROGRESS)')
parser.add_argument('-n','--neutrino', action='store_true', help='NeutrinoAPI Lookup. (WORK IN PROGRESS)')

#
# MAIN PROGRAM
#

# Parse command line arguments.
args = parser.parse_args()

# Parse Configuration File
ConfigFile = ConfigParser.ConfigParser()
ConfigFile.read(args.ConfigurationFile)

# Setup the headers list
Headers = []

# Setup the data list
Data = []

# MODULES:  Setup additional intelligence source modules here

# Pull GeoIP2 City Database Path
geoip2citydb = ConfigFile.get('GeoIP2','City_Path')

# Setup GeoIP object
try:    
    GeoIP = libs.geoip.GeoIP(geoip2citydb)
except:
    print("ERROR:  Cannot open GeoIP Database!")
    exit(1)

# Pull the VirusTotal config
vtpublicapi = ConfigFile.get('VirusTotal','PublicAPI')

# Pull the PassiveTotal config
ptusername = ConfigFile.get('PassiveTotal','Username')
ptpublicapi = ConfigFile.get('PassiveTotal','PublicAPI')
    
# Open file and read into list named hosts
try:
    with open(args.InputFile) as infile:
        hosts = infile.read().splitlines()
except:
    print("ERROR: Cannot open InputFile!")
    exit(1)
    
# Setup CSV to STDOUT
output = csv.writer(sys.stdout)

# Add standard header info
Headers.append('Input Host')

# Print Header Flag
PrintHeaders = True

# Iterate through all of the input hosts
for host in hosts:
    # Clear the row
    row = []
    
    # Add the host to the output
    row.append(host)

    # Lookup DNS
    if args.dns or args.all:
        DNSInfo = libs.dnsinfo.DNSInfo()
        if PrintHeaders:
            DNSInfo.add_headers(Headers)
        DNSInfo.add_row(host,row)
    
    # Lookup GeoIP
    if PrintHeaders:
        GeoIP.add_headers(Headers)
    GeoIP.add_row(host,row)

    # Lookup VirusTotal
    if args.virustotal or args.all:
        VT = libs.vt.VT(vtpublicapi)
        if PrintHeaders:
            VT.add_headers(Headers)
        VT.add_row(host,row)

    # Lookup PassiveTotal
    if args.passivetotal or args.all:
        PT = libs.pt.PT(ptusername,ptpublicapi)
        if PrintHeaders:
            PT.add_headers(Headers)
        PT.add_row(host,row)

    # MODULES:  Add additional intelligence source modules here
        
    # Add the row to the output data set
    Data.append(row)
    PrintHeaders = False
    
# Write the header
output.writerow(Headers)

# Write each row
for row in Data:
    output.writerow(row)

# Exit without error
exit(0)
    

