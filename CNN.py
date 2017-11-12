# -*- coding: utf-8 -*-

from gensim.models.word2vec import Word2Vec
import tensorflow as tf
#import MeCab
from janome.tokenizer import Tokenizer
import numpy as np



'''
http://tkengo.github.io/blog/2016/03/14/text-classification-by-cnn/

TODO 
テキストデータを読んで単語ごとのWordVectorの行列にして返す
W2Vのモデルを作る

文章を単語で分割しそれぞれの単語のWord2Vecの値をくっつけたものを
配列にして返却

文章数 * 単語数(100) * 50（word2vec次元数）
サイズが足りなければ(文章が短い) 0でpadding

'''
ROW_SIZE = 100
W2V_SIZE = 50      #Word2Vecの次元数[size]
def loadData():
    result = []
    tokenizer = Tokenizer()
    for doc in docs:
        tokens = tokenizer.tokenize(doc)
        r = []
        index = 0
        for token in tokens:
            if(token.part_of_speech.split(',')[0] != "記号"):
                r.extend(model.wv[token.surface])
                index+=1
                if(ROW_SIZE <= index):break
        if(0<index):
            for i in range(ROW_SIZE - index):r.extend(np.zeros(W2V_SIZE)) #Padding
            result.append(r)
    return np.array(result)


docs =[
    "最近、筆者は1人用個室の仕事場を使っているのですが、ここにGoogle Homeを設置してみました。一般のオフィスやコワーキングスペースでは難しそうですが、自分しかいない部屋なら気兼ねなく活用できます。",
    "近年、地球の衛星写真を閲覧できるサービス『Google Earth』から、謎の物体の発見報告が相次いでいる。今回は、なんと南極大陸近くの水中から”謎の巨大UFO”が発見されたというのだ"
]

model = Word2Vec.load("./word2vec.model")

data = loadData()
print(data)

# ---------------------------
# Input layer
# ---------------------------
CLASS_NUM = 3
dimX= data.shape[0]
inX = tf.placeholder(tf.float32, [None, dimX])
inY = tf.placeholder(tf.float32, [None, CLASS_NUM]) # 分類したいクラス数

print(dimX)
# ---------------------------
# Convolutional & Pooling layer
# ---------------------------
FILTER_SIZES = [ 3, 4, 5 ]
array = []
#inXv = tf.convert_to_tensor(data)

FILTER_NUM = W2V_SIZE * ROW_SIZE
x = tf.placeholder(tf.float32, [ None, dimX, FILTER_NUM, 1])

for filterSize in FILTER_SIZES:
    with tf.name_scope('conv-%d' % filterSize):
        w = tf.Variable(tf.truncated_normal(
                                [ filterSize,  FILTER_NUM, 1, FILTER_NUM],
                                stddev=0.02), name='weight')
        b  = tf.Variable(tf.constant(0.1, shape=[ FILTER_NUM ]), name='bias')
        c0 = tf.nn.conv2d(x, w, [ 1, 1, 1, 1 ], 'SAME')
        c1 = tf.nn.relu(tf.nn.bias_add(c0, b))
        c2 = tf.nn.max_pool(c1, [ 1, dimX - filterSize + 1, 1, 1 ], [ 1, 1, 1, 1 ], 'SAME')
        print(c2)
        array.append(c2)

p = tf.concat(array,3)

# ---------------------------
# Fully-connected & Output layer
# ---------------------------
keep = tf.placeholder(tf.float32)
with tf.name_scope('fc'):
    totalFilters = FILTER_NUM * len(FILTER_SIZES)
    w = tf.Variable(tf.truncated_normal([ totalFilters, CLASS_NUM ], stddev=0.02), name='weight')
    b = tf.Variable(tf.constant(0.1, shape=[ CLASS_NUM ]), name='bias')
    h0 = tf.nn.dropout(tf.reshape(p, [ -1, totalFilters ]), keep)
    predict_y = tf.nn.softmax(tf.matmul(h0, w) + b)

# ---------------------------
# Optimizer
# ---------------------------
L2_LAMBDA = 0.0001
xentropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=predict_y,labels=inY))

loss = xentropy + L2_LAMBDA * tf.nn.l2_loss(w)

global_step = tf.Variable(0, name="global_step", trainable=False)
train = tf.train.AdamOptimizer(0.0001).minimize(loss, global_step=global_step)

# ----------------------------------------------------------
# Measurement of accuracy and summary for TensorBoard.
# ----------------------------------------------------------
predict  = tf.equal(tf.argmax(predict_y, 1), tf.argmax(inY, 1))
accuracy = tf.reduce_mean(tf.cast(predict, tf.float32))

loss_sum   = tf.summary.scalar('train loss', loss)
accr_sum   = tf.summary.scalar('train accuracy', accuracy)
t_loss_sum = tf.summary.scalar('general loss', loss)
t_accr_sum = tf.scalar_summary('general accuracy', accuracy)

saver = tf.train.Saver()

# ----------------------------------------------------------
# Start TensorFlow Session.
# ----------------------------------------------------------
with tf.Session() as sess:
    sess.run(tf.initialize_all_variables())
    writer = tf.train.SummaryWriter(SUMMARY_LOG_DIR, sess.graph_def)

    train_x_length = len(train_x)
    batch_count = int(train_x_length / NUM_MINI_BATCH) + 1

    log('Start training.')
    log('     epoch: %d' % NUM_EPOCHS)
    log('mini batch: %d' % NUM_MINI_BATCH)
    log('train data: %d' % train_x_length)
    log(' test data: %d' % len(test_x))
    log('We will loop %d count per an epoch.' % batch_count)

    # Start training. We will loop some epochs.
    for epoch in xrange(NUM_EPOCHS):
        # Randomize training data every epoch in order to converge training more quickly.
        random_indice = np.random.permutation(train_x_length)

        # Split training data into mini batch for SGD.
        log('Start %dth epoch.' % (epoch + 1))
        for i in xrange(batch_count):
            # Take mini batch from training data.
            mini_batch_x = []
            mini_batch_y = []
            for j in xrange(min(train_x_length - i * NUM_MINI_BATCH, NUM_MINI_BATCH)):
                mini_batch_x.append(train_x[random_indice[i * NUM_MINI_BATCH + j]])
                mini_batch_y.append(train_y[random_indice[i * NUM_MINI_BATCH + j]])

            # TRAINING.
            _, v1, v2, v3, v4 = sess.run(
                [ train, loss, accuracy, loss_sum, accr_sum ],
                feed_dict={ input_x: mini_batch_x, input_y: mini_batch_y, keep: 0.5 }
            )
            log('%4dth mini batch complete. LOSS: %f, ACCR: %f' % (i + 1, v1, v2))

            # Write out loss and accuracy value into summary logs for TensorBoard.
            current_step = tf.train.global_step(sess, global_step)
            writer.add_summary(v3, current_step)
            writer.add_summary(v4, current_step)

            # Save all variables to a file every checkpoints.
            if current_step % CHECKPOINTS_EVERY == 0:
                saver.save(sess, CHECKPOINTS_DIR + '/model', global_step=current_step)
                log('Checkout was completed.')

            # Evaluate the model by test data every evaluation point.
            if current_step % EVALUATE_EVERY == 0:
                random_test_indice = np.random.permutation(100)
                random_test_x = test_x[random_test_indice]
                random_test_y = test_y[random_test_indice]

                v1, v2, v3, v4 = sess.run(
                    [ loss, accuracy, t_loss_sum, t_accr_sum ],
                    feed_dict={ input_x: random_test_x, input_y: random_test_y, keep: 1.0 }
                )
                log('Testing... LOSS: %f, ACCR: %f' % (v1, v2))
                writer.add_summary(v3, current_step)
                writer.add_summary(v4, current_step)

    # Save the model before the program is finished.
saver.save(sess, CHECKPOINTS_DIR + '/model-last')







