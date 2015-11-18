# DumbKeyboard v1.0 by Cory <babylonstudio@gmail.com>

class DumbKeyboard:

        clients = ['Plex for iOS', 'Plex Media Player', 'Plex Web']
        KEYS = list('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+,./<>?')

        def __init__(self, prefix, oc, callback, dktitle=None, dkthumb=None, **kwargs):

                Route.Connect(prefix+'/dumbkeyboard',                     self.Keyboard)
                Route.Connect(prefix+'/dumbkeyboard/submit',              self.Submit)
                Route.Connect(prefix+'/dumbkeyboard/history',             self.History)
                Route.Connect(prefix+'/dumbkeyboard/history/clear',       self.ClearHistory)
                Route.Connect(prefix+'/dumbkeyboard/history/add/{query}', self.AddHistory)

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
