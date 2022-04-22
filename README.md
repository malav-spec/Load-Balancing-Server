# Project 3: Load-balancing DNS servers
=====================================

Overview
--------

In project 3, we will explore a design that implements load
balancing among DNS servers by splitting the set of hostnames across
multiple DNS servers.

You will change the root server from project 1, RS, into a
load-balancing server LS, that interacts with two top-level domain
servers, TS1 and TS2. Only the TS servers store mappings from
hostnames to IP addresses; the LS does not.

Overall, you will have four programs: the client, the load-balancing
server (LS), and two DNS servers (TS1 and TS2). The client will be the
same client as project0.

Each query proceeds as follows. The client program makes the query (in
the form of a hostname) to the LS. LS then forwards the query to
one of TS1 and TS2. It must foward consistantly, for example if "google.com"
goes to TS1 before TS2 the first time it must also go to TS1
before TS2 the second time. It also must foward aproximatly half
of the queries to each server, so the load is around equal.
If and only if there is not a response from the first sever
within the timeout window, LS must ask the second server.

There are three possibilities. Either (1) LS receives a response from
the first server it asks or (2) LS receives a response from the second server it asks
or (3) LS receives a response form neither server. In case 3 LS returns an error response,
see example response for details.

If the LS receives a response (cases (1) and (2) above), it forwards
the response as is to the client. If it times out waiting for a
response (case 3) it sends an error string to the client. More details
will follow.


More details
------------

TS design
+++++++++

There are two TS servers which each maintain a DNS table consisting of
2 fields:

- Hostname
- IP address(s)

For each query received from the LS, each TS server first checks its DNS table
if the domain name is in its DNS table, it responds to the LS server immediatly
if the answer is not in the local DNS table, it asks a a domain name server for
IP addresses as in project 2 and stores them in the table, then sends the answer
from the table to the LS server.

If the answer is not in the local table,
TS1 should ask google (8.8.8.8) and TS2 should ask cloudflare (1.1.1.1)

Note that DNS lookups are case-insensitive. If there is a hit in the
local DNS table, the TS programs must respond with the version of the
string that is in their local DNS table.

Each TS maintains 2 connections -- with the LS and its authoritative server.
Note that if asked for the same ip address twice, the TS server must only ask the remote server
once, the second time it should answer from its local table

LS design
+++++++++

The LS receives queries from the client and forwards them directly to
both TS1 and TS2.

If the LS receives a response from one of the TS servers, it should
just forward the response as is to the client. (As shown above, this
string will have the same format as project 2 but without 'other'
and Hostname not found when appropriate. (see example for details)

as obtained from the TS that just responded.)

If the LS does not receive a response from either TS within a time
interval of 5 seconds (OK to wait slightly longer), the LS must send
the client the message

Hostname - Error:HOST NOT FOUND

where the Hostname is the client-requested host name.

The LS maintains three connections (and sockets): one with the client,
and one with each TS server.

The most tricky part of implementing the LS making sure you
divide the load fairly, but send the same type of queries to the
same server. You might want to look into the hash() function in python.
You must also make sure that if one of the servers crashes (or is closed)
in the middle, the LS server continues to answer queries using only the
 other server.

Client
++++++

The client is very simple. The client sends requests only to the
LS. The client also directly prints the output it receives from the
LS.

The client reads hostnames to query from PROJ3-HNS.txt, one query per
line. The client must write all the outputs it receives from LS into a
file, RESOLVED.txt, one line per query.

The client must NOT communicate directly with TS1 or TS2. The client
maintains only one connection -- with the LS.

How we will test your programs
------------------------------

As part of your submission, you will turn in three programs: ls.py, ts1.py,
and ts2.py, and one README file (more on this below). We will be
running the four programs on the ilab machines with Python 3.8.

Please do not assume that all programs will run on the same machine or that all
connections are made to the local host.  We reserve the right to test your
programs with local and remote socket connections, for example with client.py,
ts1.py, ts2.py, and ls.py each running on a different machine. You are welcome
to simplify the initial development and debugging of your project and get off
the ground by running all programs on one machine first. However, you must
eventually ensure that the programs can work across multiple machines.

The programs must work with the following command lines:

python ts1.py ts1ListenPort
python ts2.py ts2ListenPort
python ls.py lsListenPort ts1Hostname ts1ListenPort ts2Hostname ts2ListenPort
python client.py lsHostname lsListenPort

Here:

- ts1ListenPort and ts2ListenPort are ports accepting incoming connections
  at TS1 and TS2 (resp.) from LS;
- lsListenPort is the port accepting incoming connections from the
  client at LS;
- lsHostname, ts1Hostname, and ts2Hostname are the hostnames of the machines
  running LS, TS1, and TS2 (resp.).

We will provide the input file PROJ3-HNS.txt. You must populate RESOLVED.txt from the client.



Your client program should output the results to a file RESOLVED.txt, with one
line per result.

See the samples attached in this folder.

We will test your programs by running them with the hostnames and
tables in the attached input files (*.txt) as well as with new
hostnames and table configurations. You will be graded based on the
outputs in RESOLVED.txt. Your programs should not crash on correct
inputs.

README file
-----------

In addition to your programs, you must also submit a README file with clearly
dilenated sections for the following.

0. Please write down the full names and netids of all your team members.
1. Briefly discuss how you implemented the LS functionality of
   tracking which TS responded to the query and timing out if neither
   TS responded.
2. Are there known issues or functions that aren't working currently in your
   attached code (note I give half credit for any reasonably sized explained bug)?
  If so, explain.
3. What problems did you face developing code for this project?
4. What did you learn by working on this project?

Submission
----------

Turn in your project on Canvas. Only one team member needs to
submit. Please upload a single zip file consisting of ls.py,
ts1.py, ts2.py, and README.

Some hints
----------

Run your programs by first starting the TS programs, then the LS
program, and finally the client program. Brief sketches of the
interactions among the programs is attached in this folder.

There are a few methods to turn a blocking recv() call at LS into a
call that will return, possibly after a timeout. One possibility is to
use a non-blocking socket. Another is to use the system call
select(). Multi-threading may help, but is not necessary.

DNS lookups are case-insensitive.

It is okay to assume that each DNS entry or hostname is smaller than 200
characters.

START EARLY to allow plenty of time for questions should you run into
difficulties.

Try Killing the one TS server in the middle of operation to make sure
the LS server continues to operate.

Make sure no unnecesary queries are sent.
blahblahf.com
