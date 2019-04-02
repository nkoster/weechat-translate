#####################################################################
# Language translation, by Niels, niels@w3b.net, license is GPL3.   #
# v0.0.3: Updated to support Python3 -@pX <px@havok.org> 03.30.2019 #
# v0.0.4: Py3 translate would fail if input included accented       #
#       : characters -@pX <px@havok.org> 04.01.2019                 #
#       : py3-ok                                                    #
#####################################################################
# 04.01.2019: px@havok.org
#   v0.0.5  : Added auto-translate using 'langdetect'
#           : Moved some code into functions
#

# ===================[ imports ]===================
try:
    import weechat
except:
    print("WeeChat (http://weechat.org) required.")
    quit()

# langdetect required for autotranslate function to work
# `pip install langdetect`
try:
    from langdetect import detect
    from langdetect import DetectorFactory
    langdetect = True
except:
    weechat.prnt('', "'langdetect' %snot found%s, autotranslate disabled." % (weechat.color('red'), weechat.color('reset')))
    langdetect = False

# try for py3 urllib, else load py2 urllib2
try:
    import urllib.request
    ulib = urllib.request
except:
    import urllib2
    ulib = urllib2

import sys


# ===================[script info]===================
SCRIPT_NAME     = 'tr'
SCRIPT_VERSION  = '0.0.5'
SCRIPT_AUTHOR   = 'pX @ EFNet'
SCRIPT_DESC     = 'A language translator w/autotranslate'
SCRIPT_LICENSE  = 'GPL3'


# ===================[functions]===================
def tr_cb(data, buffer, args):
    a = args.split(' ')
    if len(a) < 2:
        weechat.prnt(weechat.current_buffer(), 'Usage /tr lang[,lang] text')
        return weechat.WEECHAT_RC_OK

    l = a[0]
    ol = l.split(',')
    tl = ol[0]
    o = 'en'
    if len(ol) > 1:
        o = ol[1]

    # text formatted for py2, unless we're using py3 then format accordingly
    t = ' '.join(a[1:])
    if py3():
        t = urllib.parse.quote(t)

    tr = translate(o, tl, t)

    if tr != 'en':
        if o == 'en':
            weechat.command(weechat.current_buffer(), '%s' % tr)
        else:
            weechat.prnt(weechat.current_buffer(), '/tr:\t%s' % tr)
    return weechat.WEECHAT_RC_OK


# translate outgoing message if called, or incoming if applicable
def translate(o, tl, t):
    url = 'https://translate.googleapis.com/translate_a/single' + \
        '?client=gtx&sl=' + o + '&tl=' + tl + '&dt=t&q=' + t
    url = url.replace(' ', '%20')

    req = ulib.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    response = ulib.urlopen(req)
    html = response.read()

    if py3():
        tr = html.decode().split('"')[1]
    else:
        tr = html.split('"')[1]

    return tr
    
# 'langdetect' required for this to work
def autoTrans(data, buffer, date, tags, displayed, highlight, prefix, message):
    DetectorFactory.seed = 0
    m = message.split(' ')
    # don't autotrans less than 3 words
    if len(m) >= 3:

        if py3():
            msg = message
        else:
            msg = message.decode('utf-8')

        lang = detect(msg)

        if lang != 'en':
            o = lang
            tl = 'en'
            t = message
            if py3():
                t = urllib.parse.quote(message)

            tr = translate(o, tl, t)

            # langdetect can be inaccurate with short sentences or l33t sp34k, it will send to
            # google for translation but google will return the original string with first letter
            # .upper().  Strip first character and check to see if we're in the original query
            if tr[1:] in msg:
                return weechat.WEECHAT_RC_OK

            weechat.prnt(buffer, "[autotr]\t%s" % (tr))

    return weechat.WEECHAT_RC_OK


def py3():
    if sys.version_info >= (3,0):
        return True


def timer_cb(data, remaining_calls):
    weechat.prnt(weechat.current_buffer(), '%s' % data)
    return weechat.WEECHAT_RC_OK


# ===================[main stuff]===================
if __name__ == '__main__':
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, '', ''):
        weechat.hook_timer(2000, 0, 1, 'timer_cb', '/tr:\t/tr, Google Translate in Weechat')

        weechat.hook_command(SCRIPT_NAME, SCRIPT_DESC, 'lang[,lang] text',
            'Language codes: https://sites.google.com/site/tomihasa/google-language-codes\n'
            'Github: https://github.com/nkoster/weechat-translate', '', 'tr_cb', '')

        # if 'langdetect' library is installed, hook incoming messages to autoTrans()
        if langdetect:
            weechat.hook_print('', 'notify_message', '', 1, 'autoTrans', '')
