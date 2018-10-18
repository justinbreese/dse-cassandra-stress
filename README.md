# Public cloud provider `cassandra-stress` testing
* I wanted to run some `cassandra-stress` testing on the three main cloud providers (Google, Amazon, and Microsoft) on similarly sized DataStax Enterprise clusters and see what the results would be
* Why did I want to do this? When running on a cluster of similarly-sized VMs, networking starts to come into play for replication, storage, and stronger consistency levels. This type of an exercise exposes the network so you can understand what you may have to contend with for a specific cloud provider versus another
* This is also a tutorial on some of the fun switches that you can use to tune your `cassandra-stress` test
* This is not a tutorial on how to deploy the VMs, if you want that information, please go over to another repo of mine as I repurposed it. It is 99% similar; I just didn't enable SSL and installed `dse-full`: https://github.com/justinbreese/dse-multi-cloud-demo

## Methodology
* Setup 4 VMs on each of the cloud providers; VM size was as close as possible with similar storage provisioned: i3.4xl, Standard_DS14_v2, and n1-highmem-16
* 3 of the VMs will be running DataStax Enterprise as their own cluster; again each cloud is their own cluster
* The 4th VM runs DataStax OpsCenter and acts as a `cassandra-stress` client
![Screenshot](architecture.jpg)
* Next, I ran this test on each of the clients 35 times: `cassandra-stress user profile=stress.yaml n=1000000 ops\(insert=3,likelyquery1=1\) cl=QUORUM -mode native cql3 user=cassandra password=datastax -node 104.196.140.126 -rate threads\>=121`
  * I then captured the results into an Excel file
* Then I decided to really turn it up and do 1B operations; and it led to this test that was run once on each of the clients: `nohup cassandra-stress user profile=stress.yaml n=1000000000 ops\(insert=3,likelyquery1=1\) cl=QUORUM -mode native cql3 user=cassandra password=datastax -node 40.118.149.27 -rate threads=300 -log file=output.txt -errors ignore`
  * Again, I captured the results in an Excel file

## Breakdown the switches!
I told you that this would be educational!

### First test
`cassandra-stress user profile=stress.yaml n=1000000 ops\(insert=3,likelyquery1=1\) cl=QUORUM -mode native cql3 user=cassandra password=datastax -node 104.196.140.126 -rate threads\>=121`

* `profile=stress.yaml` --> take a look at the one that I created in the root of this repo. I went to a colleague's website and was able to build it in a few minutes (source below). Do this to create the actual data model that you want to use in production!
* `n=1000000` --> the amount of times that you want to run operations
* `ops\(insert=3,likelyquery1=1\)` --> the ratio of writes:reads that you want done for your test. This is a 3:1 ratio. You can be specific about the reads that you want done. In `stress.yaml`, towards the bottom, there is a query called `likelyquery` that I want to run for my reads. You can customize this to read whatever query you prefer; super useful!
* `cl=QUORUM` --> consistency level. I see way too many stress tests done just at a consistency level of `CL=ONE`. The reality is that most don't run with a `CL=ONE` when they're in production; so why would they test against it now. Run your test against the consistency level that you want to run in production!
*  `-mode native cql3 user=cassandra password=datastax` --> you need the client to be able to access DataStax Enterprise, so ensure it has the correct username and password to do so
* `-node 104.196.140.126` --> as I am running on a client, I need to be able to connect to the cluster. This IP address was of one of the seed nodes for the cluster that I was targeting. Once I point it towards one node, the client will become aware of all of the other nodes via gossip.
* `-rate threads\>=121` --> this runs the test at thread levels that are greater than or equal to 121. You can run at less than that, but I wanted to run at realistic levels.
  * A great first test is to run at `-rate auto` which will will start at a single digit thread count and work its way up as high as it can go. This is great for understanding what is going on so you can understand the relationship for latency, operations/second, threadcount, etc.

## Second test
I am not going to go over the flags/arguments that I went over in the previous example. Instead, I'll go over the new ones or changes.

`nohup cassandra-stress user profile=stress.yaml n=1000000000 ops\(insert=3,likelyquery1=1\) cl=QUORUM -mode native cql3 user=cassandra password=datastax -node 40.118.149.27 -rate threads=300 -log file=output.txt -errors ignore`

* `nohup` --> I nohup'd because I wanted this to run as its own process. The advantage here is that it will run after I exit the session, computer goes to sleep, etc.
* `n=1000000000` --> increased the ops to 1B
* `-rate threads=300` --> set the thread count to an even 300. This is generally a point at which we start to see saturation, contention, etc.; so I wanted to stay in that range for an extended period of time
* `-log file=output.txt` --> as this would be a long running test, I wanted to be able to save the output all into a file that way I could `SCP` it back to my laptop for analysis in Excel. Otherwise it will just print to the screen; and after 1B transactions, that gets messy!
* `-errors ignore` --> after you run 1B transactions, you will get errors eventually. Cassandra handles them just fine, but you don't want it to stop the test. Do this for your tests! Otherwise, you could have your test stop half-way through; ask me how I know...

## Results
to be continued... maybe, if I can.

# Resources
* If you want to learn more about `cassandra-stress`, then look no further than the excellent work of my colleague: https://www.datastax.com/dev/blog/data-modeler
* The actual tool that builds out the `stress.yaml`: https://www.sestevez.com/sestevez/CassandraDataModeler/

# In closing
Thanks for taking a look at this repo and let me know if you have any questions.
