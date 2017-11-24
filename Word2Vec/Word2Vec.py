import MeCab
import re
from gensim.models.word2vec import Word2Vec
import numpy as np
import tensorflow as tf

TEXT_LENGTH = 100 #1文章の最大単語数
WORD_VECTER_SIZE = 500 #Word2Vecの次元数

def split_text(text):
    # Execute wakati / mecab-ipadic-neologd
    tagger = MeCab.Tagger("-Owakati -d /usr/lib/mecab/dic/mecab-ipadic-neologd")
    tagger.parse('') # For mecab bug :<
    result = tagger.parse(text)
    ws = re.compile(" ")
    words = ws.split(result)
    if words[-1] == u"\n":
        words = words[:-1]
    return words

def text2vec(texts):
    model = Word2Vec.load("./word2vec-model-builder/output/word2vec.gensim.model")
    result = []
    for text in texts:
        r = []
        index = 0
        for word in text[:TEXT_LENGTH]:
            try:
                r.append(model.wv[word])
            except:
                r.append(np.zeros(WORD_VECTER_SIZE))
        if(len(text) < TEXT_LENGTH):
            for i in range(TEXT_LENGTH - len(text)):r.append(np.zeros(WORD_VECTER_SIZE)) #Padding
        result.append(r)
    return np.array(result)

def conv_net(input_x, n_classes, dropout, reuse, is_training):
    with tf.variable_scope('CNN', reuse=reuse):
        x = tf.reshape(input_x["vectered_texts"], shape=[-1, TEXT_LENGTH, WORD_VECTER_SIZE, 1])
        x = tf.cast(x, tf.float32)
        #tensor -1x100x500x1
        print(x)
        #============================================
        # Hidden Layers
        #============================================

        # Convolution1 Layer
        #--------------------------------------------
        conv1 = tf.layers.conv2d(x, filters=32, kernel_size=5, padding='same', activation=tf.nn.relu)
        conv1 = tf.layers.max_pooling2d(conv1, 2, 2)
        print(conv1)

        # Convolution2 Layer
        #--------------------------------------------
        conv2 = tf.layers.conv2d(conv1, filters=64, kernel_size=5, padding='same', activation=tf.nn.relu)
        conv2 = tf.layers.max_pooling2d(conv2, 2, 2)
        print(conv2)

        # Fully connected layer
        #--------------------------------------------
        fc1 = tf.contrib.layers.flatten(conv2)
        fc1 = tf.layers.dense(fc1, 2048)
        print(fc1)

        # Dropout layer
        #--------------------------------------------
        fc1 = tf.layers.dropout(fc1, rate=dropout, training=is_training)
        print(fc1)

        #============================================
        # Output Layer
        #============================================
        out = tf.layers.dense(fc1, n_classes)

    return out

def model_fn(features, labels, mode):
    logits_train = conv_net(features, NUM_CLASSES, DROP_OUT, reuse=False,
                            is_training=True)
    logits_test = conv_net(features, NUM_CLASSES, DROP_OUT, reuse=True,
                           is_training=False)

    pred_classes = tf.argmax(logits_test, axis=1)
    pred_probas = tf.nn.softmax(logits_test)

    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode, predictions=pred_classes)

    loss_op = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(
        logits=logits_train, labels=tf.cast(labels, dtype=tf.int32)))
    optimizer = tf.train.AdamOptimizer(learning_rate=LEARNING_RATE)
    train_op = optimizer.minimize(loss_op,
                                  global_step=tf.train.get_global_step())

    acc_op = tf.metrics.accuracy(labels=labels, predictions=pred_classes)

    estim_specs = tf.estimator.EstimatorSpec(
        mode=mode,
        predictions=pred_classes,
        loss=loss_op,
        train_op=train_op,
        eval_metric_ops={'accuracy': acc_op})

    return estim_specs

NUM_CLASSES = 10
DROP_OUT = 0.5
LEARNING_RATE = 0.0001

def main():
    #============================================
    # Input Layer
    #============================================
    dummy_texts = [
        "四国アイランドリーグplusの徳島は１８日、鈴木康友ヘッドコーチ（５８）が今季限りで退団すると発表した。",
        "米国のドナルド・トランプ（Donald Trump）大統領は17日、ジンバブエで狩猟したゾウの体の一部を記念品として米国に持ち込むことについて許可するとした自らの政権の判断を発表からわずか1日で覆し、当面は輸入禁止を維持する姿勢を明らかにした。",
        "狩野は、メンズ専門メイクスタジオ「粋華男（イケメン）製作所」のＣＭ撮影を行ったと報告し「本当、短時間でだいぶ変わりました。って言っても、整形とかではなく、薄いメイクだけ。。前よりも華やかになった感じ。。結婚式や、パーティや、免許証や就職活動の証明写真を撮りに行く前とかにイケメンにしてもらうのに、いいと思います」とアピールした。"
    ]
    splited_texts = [ split_text(t) for t in dummy_texts ]
    vectered_texts = text2vec(splited_texts)
    #text num * TEXT_LENGTH * WORD_VECTER_SIZE
    print(len(vectered_texts),"x",len(vectered_texts[0]),"x",len(vectered_texts[0][0]))

    model = tf.estimator.Estimator(model_fn)

    batch_size = 2
    num_steps = 1000
    input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"vectered_texts":vectered_texts}, y=np.array([0,1,2]),
        batch_size=batch_size, num_epochs=None, shuffle=False)
    model.train(input_fn, steps=num_steps)

    input_fn = tf.estimator.inputs.numpy_input_fn(
        x={'vectered_texts': vectered_texts}, y=np.array([0,1,2]),
        batch_size=batch_size, shuffle=False)
    e = model.evaluate(input_fn)
    print("Testing Accuracy:", e['accuracy'])


if __name__ == "__main__":
    main()
