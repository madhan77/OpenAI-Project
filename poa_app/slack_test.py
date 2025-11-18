{\rtf1\ansi\ansicpg1252\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 Menlo-Regular;}
{\colortbl;\red255\green255\blue255;\red183\green111\blue179;\red24\green24\blue24;\red193\green193\blue193;
\red67\green192\blue160;\red89\green138\blue67;\red66\green179\blue255;\red202\green202\blue202;\red140\green211\blue254;
\red212\green214\blue154;\red194\green126\blue101;\red70\green137\blue204;\red167\green197\blue152;}
{\*\expandedcolortbl;;\cssrgb\c77255\c52549\c75294;\cssrgb\c12157\c12157\c12157;\cssrgb\c80000\c80000\c80000;
\cssrgb\c30588\c78824\c69020;\cssrgb\c41569\c60000\c33333;\cssrgb\c30980\c75686\c100000;\cssrgb\c83137\c83137\c83137;\cssrgb\c61176\c86275\c99608;
\cssrgb\c86275\c86275\c66667;\cssrgb\c80784\c56863\c47059;\cssrgb\c33725\c61176\c83922;\cssrgb\c70980\c80784\c65882;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs24 \cf2 \cb3 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 import\cf4 \strokec4  \cf5 \strokec5 os\cf4 \cb1 \strokec4 \
\cf2 \cb3 \strokec2 import\cf4 \strokec4  \cf5 \strokec5 json\cf4 \cb1 \strokec4 \
\cf2 \cb3 \strokec2 from\cf4 \strokec4  \cf5 \strokec5 urllib\cf4 \strokec4  \cf2 \strokec2 import\cf4 \strokec4  \cf5 \strokec5 request\cf4 \cb1 \strokec4 \
\
\pard\pardeftab720\partightenfactor0
\cf6 \cb3 \strokec6 # Get webhook URL from environment\cf4 \cb1 \strokec4 \
\pard\pardeftab720\partightenfactor0
\cf7 \cb3 \strokec7 WEBHOOK_URL\cf4 \strokec4  \cf8 \strokec8 =\cf4 \strokec4  \cf5 \strokec5 os\cf4 \strokec4 .\cf9 \strokec9 environ\cf4 \strokec4 .\cf10 \strokec10 get\cf4 \strokec4 (\cf11 \strokec11 "POA_SLACK_WEBHOOK_URL"\cf4 \strokec4 )\cb1 \
\pard\pardeftab720\partightenfactor0
\cf2 \cb3 \strokec2 if\cf4 \strokec4  \cf12 \strokec12 not\cf4 \strokec4  \cf7 \strokec7 WEBHOOK_URL\cf4 \strokec4 :\cb1 \
\pard\pardeftab720\partightenfactor0
\cf4 \cb3     \cf2 \strokec2 raise\cf4 \strokec4  \cf5 \strokec5 RuntimeError\cf4 \strokec4 (\cf11 \strokec11 "POA_SLACK_WEBHOOK_URL environment variable not set."\cf4 \strokec4 )\cb1 \
\
\pard\pardeftab720\partightenfactor0
\cf9 \cb3 \strokec9 payload\cf4 \strokec4  \cf8 \strokec8 =\cf4 \strokec4  \{\cb1 \
\pard\pardeftab720\partightenfactor0
\cf4 \cb3     \cf11 \strokec11 "channel"\cf4 \strokec4 : \cf11 \strokec11 "#all-openai-project"\cf4 \strokec4 ,\cb1 \
\cb3     \cf11 \strokec11 "text"\cf4 \strokec4 : \cf11 \strokec11 "Hello from your OpenAI Project prototype!"\cf4 \strokec4 ,\cb1 \
\cb3 \}\cb1 \
\
\pard\pardeftab720\partightenfactor0
\cf9 \cb3 \strokec9 req\cf4 \strokec4  \cf8 \strokec8 =\cf4 \strokec4  \cf5 \strokec5 request\cf4 \strokec4 .\cf5 \strokec5 Request\cf4 \strokec4 (\cb1 \
\pard\pardeftab720\partightenfactor0
\cf4 \cb3     \cf7 \strokec7 WEBHOOK_URL\cf4 \strokec4 ,\cb1 \
\cb3     \cf9 \strokec9 data\cf8 \strokec8 =\cf5 \strokec5 json\cf4 \strokec4 .\cf10 \strokec10 dumps\cf4 \strokec4 (\cf9 \strokec9 payload\cf4 \strokec4 ).\cf10 \strokec10 encode\cf4 \strokec4 (\cf11 \strokec11 "utf-8"\cf4 \strokec4 ),\cb1 \
\cb3     \cf9 \strokec9 headers\cf8 \strokec8 =\cf4 \strokec4 \{\cf11 \strokec11 "Content-Type"\cf4 \strokec4 : \cf11 \strokec11 "application/json"\cf4 \strokec4 \},\cb1 \
\cb3 )\cb1 \
\
\pard\pardeftab720\partightenfactor0
\cf2 \cb3 \strokec2 try\cf4 \strokec4 :\cb1 \
\pard\pardeftab720\partightenfactor0
\cf4 \cb3     \cf2 \strokec2 with\cf4 \strokec4  \cf5 \strokec5 request\cf4 \strokec4 .\cf10 \strokec10 urlopen\cf4 \strokec4 (\cf9 \strokec9 req\cf4 \strokec4 , \cf9 \strokec9 timeout\cf8 \strokec8 =\cf13 \strokec13 5.0\cf4 \strokec4 ) \cf2 \strokec2 as\cf4 \strokec4  \cf9 \strokec9 response\cf4 \strokec4 :\cb1 \
\cb3         \cf10 \strokec10 print\cf4 \strokec4 (\cf12 \strokec12 f\cf11 \strokec11 "Slack response: \cf12 \strokec12 \{\cf9 \strokec9 response\cf4 \strokec4 .status\cf12 \strokec12 \}\cf11 \strokec11  \cf12 \strokec12 \{\cf9 \strokec9 response\cf4 \strokec4 .read().decode(\cf11 \strokec11 'utf-8'\cf4 \strokec4 )\cf12 \strokec12 \}\cf11 \strokec11 "\cf4 \strokec4 )\cb1 \
\pard\pardeftab720\partightenfactor0
\cf2 \cb3 \strokec2 except\cf4 \strokec4  \cf5 \strokec5 Exception\cf4 \strokec4  \cf2 \strokec2 as\cf4 \strokec4  \cf9 \strokec9 exc\cf4 \strokec4 :\cb1 \
\pard\pardeftab720\partightenfactor0
\cf4 \cb3     \cf10 \strokec10 print\cf4 \strokec4 (\cf12 \strokec12 f\cf11 \strokec11 "Slack webhook error: \cf12 \strokec12 \{\cf9 \strokec9 exc\cf12 \strokec12 \}\cf11 \strokec11 "\cf4 \strokec4 )\cb1 \
}