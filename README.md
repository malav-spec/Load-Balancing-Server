Load-balancing DNS servers
=====================================

Overview
--------

We will explore a design that implements load
balancing among DNS servers by splitting the set of hostnames across
multiple DNS servers.

You will change the root server from project 1, RS, into a
load-balancing server LS, that interacts with two top-level domain
servers, TS1 and TS2. Only the TS servers store mappings from
hostnames to IP addresses; the LS does not.

Each query proceeds as follows. The client program makes the query (in
the form of a hostname) to the LS. LS then forwards the query to
one of TS1 and TS2. It must foward consistantly, for example if "google.com"
goes to TS1 before TS2 the first time it must also go to TS1
before TS2 the second time. It also must foward aproximatly half
of the queries to each server, so the load is around equal.
If and only if there is not a response from the first sever
within the timeout window, LS must ask the second server.


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

Client
++++++

The client is very simple. The client sends requests only to the
LS. The client also directly prints the output it receives from the
LS.
