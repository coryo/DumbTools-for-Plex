# DumbKeyboard v1.0 by Cory <babylonstudio@gmail.com>

class DumbKeyboard:

        clients = ['Plex for iOS', 'Plex Media Player', 'Plex Web']
        KEYS = list('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+,./<>?')

        def __init__(self, prefix, oc, callback, dktitle=None, dkthumb=None, **kwargs):

                cb_hash = hash(str(callback))
                Route.Connect(prefix+'/dumbkeyboard/%s'                     % cb_hash, self.Keyboard)
                Route.Connect(prefix+'/dumbkeyboard/%s/submit'              % cb_hash, self.Submit)
                Route.Connect(prefix+'/dumbkeyboard/%s/history'             % cb_hash, self.History)
                Route.Connect(prefix+'/dumbkeyboard/%s/history/clear'       % cb_hash, self.ClearHistory)
                Route.Connect(prefix+'/dumbkeyboard/%s/history/add/{query}' % cb_hash, self.AddHistory)

                oc.add(DirectoryObject(
                        key   = Callback(self.Keyboard),
                        title = str(dktitle) if dktitle else u'%s' % L('DumbKeyboard Search'),
                        thumb = dkthumb
                ))

                if not 'DumbKeyboard-History' in Dict:
                        Dict['DumbKeyboard-History'] = []
                        Dict.Save()

                self.Callback = callback
                self.callback_args = kwargs

        def Keyboard(self, query=None):

                oc = ObjectContainer()

                oc.add(DirectoryObject(
                        key   = Callback(self.Submit, query=query),
                        title = u'%s: %s' % (L('Submit'), query.replace(' ', '_') if query else query),
                ))

                if len(Dict['DumbKeyboard-History']) > 0:
                        oc.add(DirectoryObject(
                                key   = Callback(self.History),
                                title = u'%s' % L('Search History'),
                        ))

                oc.add(DirectoryObject(
                        key = Callback(self.Keyboard, query=query+" " if query else " "),
                        title = 'Space',
                ))
                
                if query:
                        oc.add(DirectoryObject(
                                key = Callback(self.Keyboard, query=query[:-1]),
                                title = 'Backspace',
                        ))

                for key in self.KEYS:
                        oc.add(DirectoryObject(
                                key   = Callback(self.Keyboard, query=query+key if query else key),
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
                                key   = Callback(self.Submit, query=item),
                                title = u'%s' % item,
                        ))

                return oc

        def ClearHistory(self):

                Dict['DumbKeyboard-History'] = []
                Dict.Save()

                return self.History()

        def AddHistory(self, query):

                if not query in Dict['DumbKeyboard-History']:
                        Dict['DumbKeyboard-History'].append(query)
                        Dict.Save()

        def Submit(self, query):

                self.AddHistory(query)

                kwargs = {'query': query}
                kwargs.update(self.callback_args)
                
                return self.Callback(**kwargs)
