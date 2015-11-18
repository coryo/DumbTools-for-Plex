# DumbKeyboard v1.0 by Cory <babylonstudio@gmail.com>

class DumbKeyboard:

        clients = ['Plex for iOS', 'Plex Media Player', 'Plex Web']
        KEYS = list('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+,./<>?')

        def __init__(self, prefix, oc, callback, dktitle=None, dkthumb=None, **kwargs):

                Route.Connect(prefix+'/dumbkeyboard',               self.Keyboard)
                Route.Connect(prefix+'/dumbkeyboard/submit',        self.Submit)
                Route.Connect(prefix+'/dumbkeyboard/history',       self.History)
                Route.Connect(prefix+'/dumbkeyboard/history/clear', self.ClearHistory)

                do = DirectoryObject()

                do.key   = Callback(self.Keyboard)
                do.title = str(dktitle) if dktitle else u'%s' % L('DumbKeyboard Search')
                if dkthumb:
                        do.thumb = dkthumb
                oc.add(do)

                if not 'DumbKeyboard-History' in Dict:
                        Dict['DumbKeyboard-History'] = []
                        Dict.Save()

                Log(Client.Product)

                self.Callback = callback
                self.callback_args = kwargs

        def Keyboard(self, q=None):

                oc = ObjectContainer()

                oc.add(DirectoryObject(
                        key   = Callback(self.Submit, q=q),
                        title = u'%s: %s' % (L('Submit'), q.replace(' ', '_') if q else q),
                ))

                if len(Dict['DumbKeyboard-History']) > 0:
                        oc.add(DirectoryObject(
                                key   = Callback(self.History),
                                title = u'%s' % L('Search History'),
                        ))

                oc.add(DirectoryObject(
                        key = Callback(self.Keyboard, q=q+" " if q else " "),
                        title = 'Space',
                ))
                if q:
                        oc.add(DirectoryObject(
                                key = Callback(self.Keyboard, q=q[:-1]),
                                title = 'Backspace',
                        ))

                for key in self.KEYS:
                        oc.add(DirectoryObject(
                                key   = Callback(self.Keyboard, q=q+key if q else key),
                                title = u'%s' % key,
                        ))

                return oc

        def History(self):

                oc = ObjectContainer()

                if len(Dict['DumbKeyboard-History']) > 0:
                        oc.add(DirectoryObject(
                                key   = Callback(self.ClearHistory),
                                title = u'%s' % L('Clear History')
                        ))

                for item in Dict['DumbKeyboard-History']:
                        oc.add(DirectoryObject(
                                key   = Callback(self.Submit, q=item),
                                title = u'%s' % item,
                        ))

                return oc

        def ClearHistory(self):

                Dict['DumbKeyboard-History'] = []
                Dict.Save()

                return self.History()

        def Submit(self, q):

                if not q in Dict['DumbKeyboard-History']:
                        Dict['DumbKeyboard-History'].append(q)
                        Dict.Save()

                kwargs = {'query': q}
                kwargs.update(self.callback_args)
                
                return self.Callback(**kwargs)
