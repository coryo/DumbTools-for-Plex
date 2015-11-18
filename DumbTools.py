# DumbPrefs v1.0 by Cory <babylonstudio@gmail.com>
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

class DumbPrefs:

        clients = ['Plex for iOS', 'Plex Media Player', 'Plex Home Theater', 'Plex for Roku']

        def __init__(self, prefix, oc, title=None, thumb=None):

                Route.Connect(prefix+'/dumbprefs/list',     self.ListPrefs)
                Route.Connect(prefix+'/dumbprefs/listenum', self.ListEnum)
                Route.Connect(prefix+'/dumbprefs/set',      self.Set)
                Route.Connect(prefix+'/dumbprefs/settext',  self.SetText)

                oc.add(DirectoryObject(
                        key   = Callback(self.ListPrefs),
                        title = title if title else L('Preferences'),
                        thumb = thumb if thumb else None,
                ))

                self.prefix = prefix
                self.host = Request.Headers['Host']

                if 'plex.direct' in self.host:
                        self.host = "%s:%s" % (self.host.split('.')[0].replace('-','.'), self.host.split(':')[-1])

                Log(self.host)

                self.GetPrefs()

        def GetPrefs(self):

                try:
                        prefs = XML.ElementFromString(HTTP.Request("http://%s/:/plugins/%s/prefs" % (self.host, Plugin.Identifier), headers=Request.Headers, immediate=True).content).xpath('/MediaContainer/Setting')
                except Exception as e:
                        Log(str(e))
                        prefs = []

                defaultPrefs = []
                for pref in prefs:
                        item = {}
                        item['id'] = pref.xpath("@id")[0]
                        item['type'] = pref.xpath("@type")[0]
                        item['label'] = pref.xpath("@label")[0]
                        item['default'] = pref.xpath("@default")[0]
                        if item['type'] == "enum":
                                item['values'] = pref.xpath("@values")[0].split("|")

                        defaultPrefs.append(item)

                self.prefs = defaultPrefs

        def Set(self, key, value):

                HTTP.Request("http://%s/:/plugins/%s/prefs/set?%s=%s" % (self.host, Plugin.Identifier, key, value), headers=Request.Headers, immediate=True)
                return self.ListPrefs()

        def ListPrefs(self):

                oc = ObjectContainer()

                for pref in self.prefs:

                        do = DirectoryObject()

                        if pref['type'] == 'enum':
                                do.key = Callback(self.ListEnum, id=pref['id'])
                        elif pref['type'] == 'bool':
                                do.key = Callback(self.Set, key=pref['id'], value=str(not Prefs[pref['id']]).lower())
                        elif pref['type'] == 'text':
                                if Client.Product in DumbKeyboard.clients:
                                        DumbKeyboard(self.prefix, oc, self.SetText, id=pref['id'],
                                                dktitle = u'%s: %s = %s' % (L(pref['label']), pref['type'], Prefs[pref['id']])
                                        )
                                else:
                                        oc.add(InputDirectoryObject(
                                                key = Callback(self.SetText, id=pref['id']),
                                                title = u'%s: %s = %s' % (L(pref['label']), pref['type'], Prefs[pref['id']])
                                        ))
                                continue
                        else:
                                do.key = Callback(self.ListPrefs)

                        do.title = u'%s: %s = %s' % (L(pref['label']), pref['type'], Prefs[pref['id']])


                        oc.add(do)

                return oc

        def ListEnum(self, id):

                oc = ObjectContainer()

                for pref in self.prefs:
                        if pref['id'] == id:
                                for i, option in enumerate(pref['values']):
                                        oc.add(DirectoryObject(
                                                key = Callback(self.Set, key=id, value=i),
                                                title = u'%s' % option,
                                        ))
                return oc

        def SetText(self, query, id):

                return self.Set(key=id, value=query)
