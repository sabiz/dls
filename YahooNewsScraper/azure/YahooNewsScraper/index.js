module.exports = function (context, myTimer) {
    const file = new Date().getTime() + ".json"
    var result = {data:[]};
    const Spider = require('node-spider');
    const spider = new Spider({
        concurrent: 1,
        delay: 100,
        allowDuplicates: false,
        catchErrors: true,
        addReferrer: false,
        xhr: false,
        keepAlive: false,
        error: function(err, url) {
            context.log(err);
            context.done();
        },
        done: function() {
            context.log(result);
            context.bindings.outputFile = result;
            context.done();
        },
    });
    const parse = function(doc) {
        doc.$('p.ttl').each(function(i, elem){
            const href = doc.$(elem).children('a').attr('href');
            const url = doc.resolve(href);
            spider.queue(url,parseItem);
        });
    };
    const parseItem = function(doc) {
        var paragraphs = 
            doc.$('p.ynDetailText').map(function(i, elem){
                return doc.$(elem).text().replace(/　/g,"").replace(/\n/g,"");
            }).get().join('');
        var title = doc.$('div.hd > h1').text();
        var r = {'title':title, 'paragraphs':paragraphs};
        result.data.push(r);

    };
    spider.queue('https://news.yahoo.co.jp/flash', parse);
};
