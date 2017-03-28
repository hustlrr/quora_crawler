a web crawler of quora.If you find any bug of this program, please tell me.Thank you.

由于quora前段使用了ajax技术，下载一个问题页面后无法得到所有答案。我的解决思路是使用selenium+phantomjs对网页进行多次刷新，当所有答案都被加载后下载网页，并使用beautifulsoup对网页进行解析
