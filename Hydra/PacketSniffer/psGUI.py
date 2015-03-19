import Tkinter
import socket, sys, time, os, pygeoip, dpkt
from struct import *

class psGUI(Tkinter.Tk):
   packets=" "
   ipLocations=" "
   downloads=" "
   attacks=" "
   def __init__(self, parent):
	Tkinter.Tk.__init__(self, parent)
	self.parent=parent
	self.initialise()

   def initialise(self):
	self.grid()

	packetbutton=Tkinter.Button(self, text=u"Packets", command=self.OnPacket)
	packetbutton.grid(column=0, row=1)
	
	ipbutton=Tkinter.Button(self, text=u"IP Locations", command=self.OnIP)
	ipbutton.grid(column=1, row=1)

	downloadbutton=Tkinter.Button(self, text=u"Downloads", command=self.OnDownload)
	downloadbutton.grid(column=2, row=1)
	
	attackbutton=Tkinter.Button(self, text=u"Attacks", command=self.OnAttack)
	attackbutton.grid(column=3, row=1)

	startbutton=Tkinter.Button(self, text=u"Start", command=self.OnStart)
	startbutton.grid(column=1, row=3)
	
	stopbutton=Tkinter.Button(self, text=u"Stop", command=self.OnStop)
	stopbutton.grid(column=2, row=3)
	
	scrollbar=Tkinter.Scrollbar(self)
	self.textbox=Tkinter.Text(self, width=150)
	scrollbar.config(command=self.textbox.yview)
	self.textbox.config(yscrollcommand=scrollbar.set)
	self.textbox.grid(column=0, row=2, columnspan=4)

   def OnStart(self):
	global ipLocations
	ipLocations="Starting packet sniffing.\n"
	global downloads
	downloads="Starting packet sniffing.\n"
	global attacks
	attacks="Starting packet sniffing.\n"
	#Convert a string of 6 characters of ethernet address into a dash separated hex string
	def eth_addr (a) :
  	   b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]) , ord(a[1]) , ord(a[2]), ord(a[3]), ord(a[4]) , ord(a[5]))
  	   return b
 
	#create a AF_PACKET type raw socket 
	#define ETH_P_ALL    0x0003          /* Every packet */
	try:
    	   s = socket.socket( socket.AF_PACKET , socket.SOCK_RAW , socket.ntohs(0x0003))
	except socket.error , msg:
	   errormsg='Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	   self.textbox.insert(Tkinter.END, errormsg)
	   self.textbox.update_idletasks()
	   return
    	   #print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    	   #sys.exit()

	timestr=time.strftime("%Y%m%d-%H%M%S")
	os.mkdir(timestr)
	pfile=open('%s/packets.txt' % timestr, 'w+')
	lfile=open('%s/ipLocations.txt' % timestr, 'w+') 
	dfile=open('%s/downloaded.txt' % timestr, 'w+')
	afile=open('%s/attackList.txt' % timestr, 'w+')
	locate=pygeoip.GeoIP('GeoLiteCity.dat')
	# receive a packet
	while True:
	    packet = s.recvfrom(65565)
     
	    #packet string from tuple
	    packet = packet[0]
     
	    #parse ethernet header
	    eth_length = 14
     
	    eth_header = packet[:eth_length]
	    eth = unpack('!6s6sH' , eth_header)
	    eth_protocol = socket.ntohs(eth[2])
	    print 'Destination MAC : ' + eth_addr(packet[0:6]) + ' Source MAC : ' + eth_addr(packet[6:12]) + ' Protocol : ' + str(eth_protocol)
	    first='Destination MAC : ' + eth_addr(packet[0:6]) + ' Source MAC : ' + eth_addr(packet[6:12]) + ' Protocol : ' + str(eth_protocol)
	    pfile.write(''+first);
	    global packets
	    packets=first
	    #Parse IP packets, IP Protocol number = 8
	    if eth_protocol == 8 :
	        #Parse IP header
	        #take first 20 characters for the ip header
	        ip_header = packet[eth_length:20+eth_length]
         
	        #now unpack them
	        iph = unpack('!BBHHHBBH4s4s' , ip_header)
	 
	        version_ihl = iph[0]
	        version = version_ihl >> 4
	        ihl = version_ihl & 0xF
	 
	        iph_length = ihl * 4
	 
	        ttl = iph[5]
	        protocol = iph[6]
	        s_addr = socket.inet_ntoa(iph[8]);
	        d_addr = socket.inet_ntoa(iph[9]);
 
	        print 'Version : ' + str(version) + ' IP Header Length : ' + str(ihl) + ' TTL : ' + str(ttl) + ' Protocol : ' + str(protocol) + ' Source Address : ' + str(s_addr) + ' Destination Address : ' + str(d_addr)
	        second=' Version : '+str(version) + ' IP Header Length : ' + str(ihl) + ' TTL : ' +str(ttl) + ' Protocol : ' + str(protocol) + ' Source Address : ' + str(s_addr) + 'Destination Address : '+str(d_addr)
		pfile.write(''+second)
		packets+=second
		print''+str(s_addr)
		if (s_addr!='127.0.0.1'):
		   s_data = locate.record_by_name(s_addr)
		   d_data = locate.record_by_name(d_addr)
		   print ''+str(s_data)
	 	   print ''+str(d_data)
		   if (s_data):
		      s_city = s_data['city']
		      s_country = s_data['country_name']
		      slocation=' Source IP Address : ' + str(s_addr) + ' Source City : ' +str(s_city) + ' Source Country : ' + str(s_country)
		      lfile.write(''+slocation)
		     # global ipLocations
		      ipLocations+=slocation
		   elif (d_data):
		        d_country = d_data['country_name']
		        d_city = d_data['city']
		        dlocation= ' Destination IP Address : ' + str(d_addr) + ' Destination City : ' + str(d_city) + ' Destination Country : ' + str(d_country) + '\n'
		  	lfile.write(''+dlocation)
		       # global ipLocations
		        ipLocations+=dlocation
		   else:  
		      s_city='Unavailable'
		      s_Country='Unavailable'
		      d_City='Unavailable'
		      d_Country='Unavailable'
		      location=' Source IP Address : ' + str(s_addr) + ' Source City : ' +str(s_city) + ' Source Country : ' + str(s_country) + ' Destination IP Address : ' + str(d_addr) + ' Destination City : ' + str(d_city) + ' Destination COuntry : ' + str(d_country) + '\n'
	              lfile.write(''+location)
		     # global ipLocations
		      ipLocations+=location
	        #TCP protocol
	        if protocol == 6 :
	            t = iph_length + eth_length
	            tcp_header = packet[t:t+20]
	 
	            #now unpack them
	            tcph = unpack('!HHLLBBHHH' , tcp_header)
             
	            source_port = tcph[0]
	            dest_port = tcph[1]
	            sequence = tcph[2]
	            acknowledgement = tcph[3]
	            doff_reserved = tcph[4]
	            tcph_length = doff_reserved >> 4
	             
	            print 'Source Port : ' + str(source_port) + ' Dest Port : ' + str(dest_port) + ' Sequence Number : ' + str(sequence) + ' Acknowledgement : ' + str(acknowledgement) + ' TCP header length : ' + str(tcph_length)
	            third='Source Port : ' + str(source_port) + 'Destination Port : ' + str(dest_port) + 'Sequence Number : ' + str(sequence) + 'Acknowledgement : ' + str(acknowledgement) + 'TCP Header Length : '+str(tcph_length) 
	            pfile.write(''+third)
		    packets+=third
		    h_size = eth_length + iph_length + tcph_length * 4
	            data_size = len(packet) - h_size
             
	            #get data from the packet
	            data = packet[h_size:]
             
	            print 'Data : ' + data
		    fourth='Data : ' + data + '\n'
		    pfile.write(''+fourth)
		    packets+=fourth
		    try:
	               http=dpkt.http.Request(''+data)
		       print ''+str(http)
		       print 'Before Get if statement'
		       if (http.method=='GET'):
		           print 'Inside Get if statement'
		           uri=http.uri.lower()
		           print ''+str(uri)
		           if '.zip' in uri and 'loic' in uri:
		             downloaded= 'IP Address : ' + str(s_addr) + ' Downloaded Loic\n'
		             dfile.write(''+downloaded)
			     downloads+=downloaded
	            except:
			pass
		    try:
		       http=dpkt.http.Request(''+data)
		       if (dest_port ==6667):
			  if ('!lazor' in data):
			     attack='DDOS Hivemind issued by : ' + str(s_addr) + '\n'
			     afile.write(''+attack)
			     attacks+=attack
		       elif (source_port ==6667):
			   if ('!lazor' in data):
			      attack='DDOS Hivemind isued to : ' + str(s_addr) + '\n'
			      afile.write(''+attack)
			      attacks+=attack
		    except:
			pass
	        #ICMP Packets
	        elif protocol == 1 :
	            u = iph_length + eth_length
	            icmph_length = 4
	            icmp_header = packet[u:u+4]
 
	            #now unpack them :)
	            icmph = unpack('!BBH' , icmp_header)
	             
	            icmp_type = icmph[0]
	            code = icmph[1]
	            checksum = icmph[2]
	             
	            print 'Type : ' + str(icmp_type) + ' Code : ' + str(code) + ' Checksum : ' + str(checksum)
	            fifth='TYpe : ' + str(icmp_type) + ' COde : ' + str(code) + 'Checksum : ' + str(checksum) 
	            pfile.write(''+fifth)
		    packets+=fifth

		    h_size = eth_length + iph_length + icmph_length
	            data_size = len(packet) - h_size
             
	            #get data from the packet
	            data = packet[h_size:]
             
	            print 'Data : ' + data
		    sixth='Data : ' + data + '\n'
		    pfile.write(''+sixth)
		    packets+=sixth
	    
	        #UDP packets
	        elif protocol == 17 :
	            u = iph_length + eth_length
	            udph_length = 8
	            udp_header = packet[u:u+8]
 
	            #now unpack them 
	            udph = unpack('!HHHH' , udp_header)
             
	            source_port = udph[0]
	            dest_port = udph[1]
	            length = udph[2]
	            checksum = udph[3]
             
	            print 'Source Port : ' + str(source_port) + ' Dest Port : ' + str(dest_port) + ' Length : ' + str(length) + ' Checksum : ' + str(checksum)
		    seventh='Source Port : ' + str(source_port) + 'Destination Port : ' + str(dest_port) + 'Length : ' + str(length) + 'Checksum : ' + str(checksum)             
	            pfile.write(''+seventh)
		    packets+=seventh
		    h_size = eth_length + iph_length + udph_length
	            data_size = len(packet) - h_size
             
	            #get data from the packet
	            data = packet[h_size:]
             
	            print 'Data : ' + data
		    eigth='Data : ' + data + '\n'
		    pfile.write(''+eigth)
		    packets+=eigth
	    
	        #some other IP packet like IGMP
	        else :
	            print 'Protocol other than TCP/UDP/ICMP'
             
	        print
		self.textbox.insert(Tkinter.END, packets)
		self.textbox.update_idletasks()

   def OnStop(self):
	pass

   def OnPacket(self):
	global packets
	self.textbox.delete(1.0, Tkinter.END)
	self.textbox.update_idletasks()
	self.textbox.insert(Tkinter.END, packets)
	self.textbox.update_idletasks()

   def OnIP(self):
	global ipLocations
	self.textbox.delete(1.0, Tkinter.END)
	self.textbox.update_idletasks()
	self.textbox.insert(Tkinter.END, ipLocations)
	self.textbox.update_idletasks()

   def OnDownload(self):
	global downloads
	self.textbox.delete(1.0, Tkinter.END)
	self.textbox.update_idletasks()
	self.textbox.insert(Tkinter.END, downloads)
	self.textbox.update_idletasks()

   def OnAttack(self):
	global attacks
	self.textbox.delete(1.0, Tkinter.END)
	self.textbox.update_idletasks()
	self.textbox.insert(Tkinter.END, attacks)
	self.textbox.update_idletasks()

if __name__=="__main__":
   app=psGUI(None)
   app.title('Packet Sniffer')
   app.mainloop()
