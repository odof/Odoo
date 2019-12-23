# -*- coding: utf-8 -*-

from odoo import api, fields, models

import re


class OFWebsiteSupportTicketMerge(models.TransientModel):
    _name = 'of.website.support.ticket.merge'

    @api.model
    def _default_partner_id(self):
        tickets = self.env[self._context['active_model']].browse(self._context['active_ids'])
        partner = tickets and tickets[0].partner_id
        for ticket in tickets:
            if ticket.partner_id != partner:
                partner = False
                break
        return partner and partner.id or False

    partner_id = fields.Many2one(
        'res.partner', string="Contact", default=lambda s: s._default_partner_id(), readonly=True)

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        tickets = self.env[self._context['active_model']].browse(self._context['active_ids'])
        tickets = tickets.sorted('id')

        new_ticket = tickets[0]
        old_tickets = tickets[1:]
        # Déplacement du fil de discussion
        old_tickets.mapped('message_ids').write({'res_id': new_ticket.id})
        # Déplacement des pièces jointes
        old_tickets.mapped('attachment_ids').write({'res_id': new_ticket.id})

        old_tickets.sudo().unlink()

        action = self.env.ref('website_support.website_support_ticket_action').read()[0]
        action['views'] = [(self.env.ref('website_support.website_support_ticket_view_form').id, 'form')]
        action['res_id'] = new_ticket.id
        return action
