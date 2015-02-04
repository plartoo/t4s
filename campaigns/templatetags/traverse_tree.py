from django import template
from smsmessages.models import Message
from django.core.urlresolvers import reverse


register = template.Library()

# TODO: refactor this ugly hack (maybe not if I eventually end up replacing it with JSPlumb or equivalent)
def traverse_tree(root_message, campaign_id):
    tree_html = ''
    add_option_link = '<a href="%s?msg_id=%s&cam_id=%s">Add options for message above</a>'%(reverse('campaigns:create_multiple_msg_conv'), root_message.id, campaign_id)
    copy_this_msg = '&nbsp;|&nbsp;<a href="%s?msg_id=%s&cam_id=%s">Copy above message as the root of a new conversation</a>'%(reverse('campaigns:duplicate_campaign'), root_message.id, campaign_id)
    tree_html += '<ul><b>Prompting Message: </b>' + root_message.content + '<span class="action-btns">' + add_option_link + copy_this_msg + '</span>'
    options = root_message.options.all()
    if options:
        for option in options:
            # Note: I can put another condition to remove trigger keyword if it is '*', but this ugly code is temporary, so won't waste time and make it even uglier
            tree_html += '<li><b>Option:</b> %s%s%s</li>'%(option.trigger_keyword, option.separator, option.option_content)
            tree_html += traverse_tree(option.child_msg, campaign_id)
    tree_html += '</ul>'
    return tree_html

#Msg 1 ==> Msg 2 ==> Msg 1 
class TreeNode(template.Node):
    def __init__(self, msg_id_name, cam_id_name):
        self.msg_id_name = msg_id_name
        self.cam_id_name = cam_id_name

    def render(self, context):
        msg_id = template.Variable(self.msg_id_name).resolve(context)
        cam_id = template.Variable(self.cam_id_name).resolve(context)
        root_message = Message.objects.get(id=msg_id)
        return traverse_tree(root_message, cam_id)


@register.tag(name="tree_nodes")
def get_all_tree_nodes(parser, token):
    # Django provides tag_name by default, but we pass in the other two; used in "messages/list.html"
    tag_name, msg_id_name, cam_id_name = token.split_contents()
    return TreeNode(msg_id_name, cam_id_name)
