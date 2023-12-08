# crawlCodingArticles
This is used for my part-time-Job. My Job is  finding and uploading proper contents for "Programmers" Company. So I automate finding job with this crawler, and this helps me to make dataSet, to be continued with DeepLearning Process. 


Whoever want to use this code can install the required packages using pip by running the following command:

pip install -r requirements.txt

And then you can run each "script_brunch.py" and "script_youtube.py" file just click "run" button of your editor.
(script_youtube_py file is required to be with your own Google API KEY)

------------------------------


+ 231208
+ Interviewer aksed me why do I use threading, and let me explain Python Global Interperter Lock(GIL) concept.
+ I cannot answer about GIL at that time, but now I can tell what it is and what does that question means.

+ Multi-threading on Python isn't working as we expected. Even though It looks like multi - thread working at same time.
+ but just one thread can work at same time. So, Multi - threading means, each thread does context-switching so fastly but just one thread works.
+ So the interviewer's Q is reasonable.

+ But In this crawling Job, each selenium virtual - browser does in this process ( crawl -> going down -> next page loading(delay - sleep) - crawl again)
+ So If I run on single thread, each waiting time is wasteful. Multi - threading could be helpful in this case.
