# DumbPrefs v1.0 by Cory <babylonstudio@gmail.com>

from DumbKeyboard import DumbKeyboard

class DumbPrefs:

        def __init__(self, prefix, oc, title=None, thumb=None):

                Route.Connect(prefix+'/dumbprefs/list',     self.ListPrefs)
                Route.Connect(prefix+'/dumbprefs/listenum', self.ListEnum)
                Route.Connect(prefix+'/dumbprefs/set',      self.Set)
                Route.Connect(prefix+'/dumbprefs/settext',  self.SetText)

                self.GetPrefs()

                oc.add(DirectoryObject(
                        key   = Callback(self.ListPrefs),
                        title = title if title else L('Preferences'),
                        thumb = thumb if thumb else None,
                ))
                Log(Request.Headers)

                self.prefix = prefix

        def GetPrefs(self):

                try:
                        prefs = XML.ElementFromString(HTTP.Request("http://%s/:/plugins/%s/prefs" % ("127.0.0.1:32400", Plugin.Identifier), headers=Request.Headers, immediate=True).content).xpath('/MediaContainer/Setting')
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

                HTTP.Request("http://%s/:/plugins/%s/prefs/set?%s=%s" % ("127.0.0.1:32400", Plugin.Identifier, key, value), headers=Request.Headers, immediate=True)
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
