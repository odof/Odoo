# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo import tools

import re

class OFWebsiteSupportMessageMove(models.TransientModel):
    _name = 'of.website.support.message.move'

    def _default_partner_id(self):
        result = False
        if self._context.get('active_model'):
            result = self.env[self._context['active_model']].browse(self._context['active_id']).partner_id.id
        return result

    ticket_id = fields.Many2one(
        'website.support.ticket', string="Ticket d'origine", required=True, ondelete='cascade',
        default=lambda s:s._context.get('active_id')
    )
    new_ticket_id = fields.Many2one(
        'website.support.ticket', string='Ticket de destination',
        domain="[('partner_id', '=', partner_id),('id', '!=', ticket_id)]"
    )
    partner_id = fields.Many2one('res.partner', default=lambda self: self._default_partner_id())
    message_ids = fields.Many2many(
        'mail.message', string='Messages', required=True, ondelete='cascade',
        domain="[('model', '=', 'website.support.ticket'), ('res_id', '=', ticket_id)]"
    )
    subject = fields.Char(string='Sujet')
    description = fields.Text(string='Description')

    @api.onchange('new_ticket_id', 'message_ids')
    def onchange_message_ids(self):
        if self.new_ticket_id:
            # Pas de création de ticket.
            return
        if self.message_ids:
            # Dans un onchange, l'ordre des éléments dépend de l'ordre de sélection et non de l'ordre de l'objet
            # On retrie donc les messages par id
            messages = self.message_ids.sorted('id', reverse=True)
            self.subject = messages[-1].subject
            self.description = "<p>===============</p>".join(tools.html_sanitize(message.body or '')
                                                             for message in messages)
        else:
            self.subject = False
            self.description = False

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        new_ticket = self.new_ticket_id
        if not new_ticket:
            new_ticket = self.env['website.support.ticket'].create({
                'partner_id': self.partner_id.id,
                'subject': self.subject,
                'description': self.description,
                'person_name': self.partner_id.name,
            })
        self.message_ids.write({'res_id': new_ticket.id})

        action = self.env.ref('website_support.website_support_ticket_action').read()[0]
        action['views'] = [(self.env.ref('website_support.website_support_ticket_view_form').id, 'form')]
        action['res_id'] = new_ticket.id
        return action

class MailMessage(models.Model):
    _inherit = 'mail.message'

    of_body_condensed = fields.Text(string=u"Contenu condensé", compute='_compute_of_body_condensed')

    @api.multi
    def _compute_of_body_condensed(self):
        for message in self:
            body = message.body
            # Retrait des sauts de ligne
            body = body.replace('\n','')
            # Transformation des paragraphes et sauts de ligne html en sauts de ligne
            body = re.sub('<br[^<]*>', '\n', body.replace('</p>', '\n'))
            # Retrait de toutes les autres balises html
            body = re.sub('<[^<]*>', '', body)
            # Retrait des doublons de sauts de ligne et espaces blancs
            body = re.sub('[ \n]*\n', '\n', body)
            body = re.sub(' +', ' ', body)
            message.of_body_condensed = body
