'''
Created on Oct 20, 2016

@author: kumaran
'''

import time,sys
import requests
sys.path.append('../PyNMRSTAR') #NMR-STAR and NEF-Parser added as a submodule and imported into this project. This is a separate git repository
import bmrb
from Bio.PDB import *
from dns.rdatatype import NULL

class NMRRestraints(object):
    '''
    classdocs
    '''
    BMRB_API_URL="http://webapi.bmrb.wisc.edu/current/jsonrpc"
    DATA_DIR="/kbaskaran/restraints/"

    def __init__(self):
        '''
        Constructor
        '''
    
    def submit_query(self,api_query):
        response = requests.post(self.BMRB_API_URL,json=api_query)
        
        if response.status_code == 403:
            print "Waiting to continue because of rate limiting."
            time.sleep(10)
            response = requests.post(self.BMRB_API_URL,json=api_query)
        
        if response.status_code != 200 :
            print "Server error : %s"% response.text
            api_data=NULL
        
        try:
            api_data=response.json()
        except Exception as e:
            print "Exception occured : %s" % str(e)
        return api_data
    
    
    BMRB_API_URL="http://webapi.bmrb.wisc.edu/current/jsonrpc"

    def read_star_file(self,fname):
        infile=self.DATA_DIR+fname
        self.starData=bmrb.Entry.from_file(infile)
    
    def get_restraint_info(self):
        
        list_entries={
                      "method": "list_entries",
                      "jsonrpc": "2.0",
                      "params":{"database":"macromolecules"},
                      "id":1
                      }
        entry_list=self.submit_query(list_entries)
        for bmrbid in entry_list['result']:
            rest_query={
                        "method":"loop",
                        "jsonrpc":"2.0",
                        "params":{
                                  "ids":[bmrbid],
                                  "keys":["_Gen_dist_constraint"]
                                  },
                        "id":1}
            out_dat=self.submit_query(rest_query)
            if out_dat['result'][bmrbid]['_Gen_dist_constraint']:
                print bmrbid


if __name__=="__main__":
    p=NMRRestraints()
    p.read_star_file("merged_34043_5lw8.str")
    #p.get_restraint_info()