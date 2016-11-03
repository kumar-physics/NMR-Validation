'''
Created on Oct 20, 2016

@author: kumaran
'''

import time,sys
import requests
from PyNMRSTAR.bmrb import Saveframe
sys.path.append('../PyNMRSTAR') #NMR-STAR and NEF-Parser added as a submodule and imported into this project. This is a separate git repository
import bmrb
from Bio.PDB import *
from dns.rdatatype import NULL
from string import atoi

class NMRRestraints(object):
    '''
    classdocs
    '''
    BMRB_API_URL="http://webapi.bmrb.wisc.edu/current/jsonrpc"
    DATA_DIR="/kbaskaran/restraints/"
    CIF_DIR="/kbaskaran/mmCIF/"
    CIF_Parser = MMCIFParser()

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
    
    def read_mmCIF(self,pdbid):
        self.struct=self.CIF_Parser.get_structure(pdbid, self.CIF_DIR+pdbid+".cif")
       #a1=self.struct[0]["A"][102]["HA"]
        #print a1
        #a2=struct[1]["A"][8]["C"]
        #print a1-a2
    
    BMRB_API_URL="http://webapi.bmrb.wisc.edu/current/jsonrpc"

    def read_star_file(self,fname):
        infile=self.DATA_DIR+fname
        self.starData=bmrb.Entry.from_file(infile)
        self.read_mmCIF('5lw8')
        for saveframe in self.starData:
            if saveframe.category=="general_distance_constraints":
                for loop in saveframe:
                    if loop.category=="_Gen_dist_constraint":
                        seq1=loop.columns.index("Auth_seq_ID_1")
                        atm1=loop.columns.index("Atom_ID_1")
                        ch1=loop.columns.index("PDB_strand_ID_1")
                        seq2=loop.columns.index("Auth_seq_ID_2")
                        atm2=loop.columns.index("Atom_ID_2")
                        ch2=loop.columns.index("PDB_strand_ID_2")
                        dis=loop.columns.index("Distance_val")
                        dl=loop.columns.index("Distance_lower_bound_val")
                        du=loop.columns.index("Distance_upper_bound_val")
                        for dat in loop.data:
                            #print dat[seq1],dat[atm1],dat[seq2],dat[atm2]
                            for modd in self.struct.get_models():
                                #print dat[ch1],dat[ch2]
                                try:
                                    a1=modd[dat[ch1]][atoi(dat[seq1])][dat[atm1]]
                                    a2=modd[dat[ch2]][atoi(dat[seq2])][dat[atm2]]
                                    if (a1-a2)>dat[du] or (a1-a2)<dat[dl]:
                                        print modd,dat[seq1],dat[atm1],dat[seq2],dat[atm2],a1-a2,dat[dis],dat[dl],dat[du]
                                except KeyError:
                                    print dat
                                    pass
    
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
    #p.read_mmCIF('2mgo')
    p.read_star_file("merged_34043_5lw8.str")
    #p.get_restraint_info()