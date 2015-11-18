# DumbKeyboard

This serves as a replacement for the InputDirectoryObject in the Plex Plug-in framework for clients that don't support it. It uses DirectoryObjects to build a query string, then lets you send that to the Search function. Search queries are saved in the channels Dict so they don't need to be re-entered.

![http://i.imgur.com/Q622vhM.png](http://i.imgur.com/Q622vhM.png)

## Usage:

add `DumbKeyboard.py` to `Channel.bundle/Contents/Code`.

in `__init__.py` add:
```
from DumbKeyboard import DumbKeyboard
```

in `__init__.py` where you have an InputDirectoryObject:
```
if Client.Product in DumbKeyboard.clients:
        DumbKeyboard(PREFIX, oc,
                dktitle  = u'%s' L('search'),
                dkthumb  = R(ICONS['search']),
                callback = Search)
else:
        oc.add(InputDirectoryObject(
                key    = Callback(Search),
                title  = u'%s' L('search'),
                prompt = 'Search',
                thumb  = R(ICONS['search'])
        ))
        
@route(PREFIX + '/search')
def Search(query):
        ...
```        
## Definitions:

`DumbKeyboard(prefix, oc, callback, dktitle=None, dkthumb=None, **kwargs)`

Appends a DirectoryObject to `oc` which will provide a series of DirectoryObjects to build a string. `callback` is called with the arguments `query` and `**kwargs` when the Submit directory is selected.

  * *prefix*: whatever is used in the @handler(PREFIX, NAME).
  * *oc*: the object container to add to.
  * *callback*: the Search function. This must have atleast 1 argument 'query'.
  * *dktitle*: (optional) the title to use for the search directoryObject.
  * *dkthumb*: (optional) the thumbnail to use for the search directoryObject.
  * ***kwargs*: additional arguments to send to the callback function.
    * if you have search function `Search(query, a=None, b=None)` then you can use `DumbKeyboard(prefix, oc, Search, a='something' b=123)`
 
`DumbKeyboard.clients` - Client.Platform's that don't have InputDirectoryObjects or don't always work correctly.
  * Plex for iOS
  * Plex Media Player
  * Plex Web
