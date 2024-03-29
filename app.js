function initViewer(ref) {
    var proto = (window.location.protocol == "https:")? "wss://": "ws://";
    var ws = new WebSocket(proto+window.location.host+"/websocket/?id="+ref);
    console.log("Connecting...");
    ws.onopen = function(evt) {
        console.log("Connected!");
    };

    ws.onmessage = function(evt) {
        var change = JSON.parse(evt.data);
        console.log(change);
        var $tag = $('#'+change.id);
        change.object = $tag;

        if (change.type === 'refresh') {
            $tag.html(change.value);
        } else if (change.type === 'trigger') {
            $tag.trigger(change.value);
        } else if (change.type === 'added') {
            $tag.append($(change.value));
        } else if (change.type === 'removed') {
            $tag.find('#'+change.value).remove();
        } else if (change.type === 'update') {
            if (change.name==="text") {
                var node = $tag.contents().get(0);
                if (!node) {
                    node = document.createTextNode("");
                    $tag.append(node);
                }
                node.nodeValue = change.value;
            } else if (change.name==="attrs") {
                $.map(change.value,function(v,k){
                    $tag.prop(k,v);
                });
            } else {
                if (change.name==="cls") {
                    change.name = "class";
                }
                $tag.prop(change.name,change.value);
            }
        } else if (change.type === 'error') {
            console.log(change.message);
        } else if (change.type === 'reload') {
            location.reload();
        } else {
            console.log("Unknown change type");
        }
    };

    ws.onclose = function(evt) {
        console.log("Disconnected!");
    };

    function sendEvent(change) {
        console.log(change);
        ws.send(JSON.stringify(change));
    };

    function sendNodeValue(){
        sendEvent({
            'id':this.id,
            'type':'update',
            'name':'value',
            'value':$(this).val(),
        });
    };

    $(document).on('click', '[clickable]',function(e){
        e.preventDefault();
        sendEvent({
            'id':this.id,
            'type':'event',
            'name':'clicked'
        });
    });
    $(document).on('change', ":checkbox", function(){
        sendEvent({
        'id':this.id,
        'type':'update',
        'name':'checked',
        'value':($(this).prop('checked'))?'checked':'',
        });
    });
    $(document).on('change', "select", sendNodeValue);
    $(document).on('input', 'input', sendNodeValue);
    $(document).on('change', 'textarea', function() {
        sendEvent({
            'id':this.id,
            'type':'update',
            'name':'text',
            'value':$(this).val(),
        });
    });

    return ws;
}
