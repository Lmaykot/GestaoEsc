import tkinter as tk
from tkinter import ttk

# Palette
C_BG       = '#F5F6FA'
C_SIDEBAR  = '#2C3E6B'
C_ACCENT   = '#3B82F6'
C_ACCENT2  = '#1E40AF'
C_WHITE    = '#FFFFFF'
C_TEXT     = '#1E293B'
C_MUTED    = '#64748B'
C_BORDER   = '#CBD5E1'
C_ROW_ODD  = '#F8FAFC'
C_ROW_EVEN = '#EFF3FB'
C_SUCCESS  = '#16A34A'
C_WARN     = '#D97706'
C_TAB_ACT  = '#FFFFFF'
C_TAB_INP  = '#E2E8F0'

FONT_TITLE  = ('Segoe UI', 16, 'bold')
FONT_H2     = ('Segoe UI', 12, 'bold')
FONT_H3     = ('Segoe UI', 10, 'bold')
FONT_BODY   = ('Segoe UI', 10)
FONT_SMALL  = ('Segoe UI', 9)
FONT_MONO   = ('Consolas', 10)


def apply_styles(root):
    style = ttk.Style(root)
    style.theme_use('clam')

    # General
    style.configure('.',
        background=C_BG, foreground=C_TEXT,
        font=FONT_BODY, borderwidth=0)

    # Notebook
    style.configure('TNotebook', background=C_SIDEBAR, borderwidth=0, tabmargins=[0, 0, 0, 0])
    style.configure('TNotebook.Tab',
        background=C_SIDEBAR, foreground='#A0AEC0',
        font=('Segoe UI', 10, 'bold'),
        padding=[18, 10], borderwidth=0)
    style.map('TNotebook.Tab',
        background=[('selected', C_BG)],
        foreground=[('selected', C_ACCENT)])

    # Frame
    style.configure('TFrame', background=C_BG)
    style.configure('Card.TFrame', background=C_WHITE, relief='flat')

    # Labels
    style.configure('TLabel', background=C_BG, foreground=C_TEXT)
    style.configure('Card.TLabel', background=C_WHITE, foreground=C_TEXT)
    style.configure('Title.TLabel', background=C_BG, foreground=C_TEXT, font=FONT_TITLE)
    style.configure('H2.TLabel', background=C_BG, foreground=C_TEXT, font=FONT_H2)
    style.configure('H2Card.TLabel', background=C_WHITE, foreground=C_TEXT, font=FONT_H2)
    style.configure('Muted.TLabel', background=C_BG, foreground=C_MUTED, font=FONT_SMALL)
    style.configure('MutedCard.TLabel', background=C_WHITE, foreground=C_MUTED, font=FONT_SMALL)
    style.configure('Accent.TLabel', background=C_WHITE, foreground=C_ACCENT, font=FONT_H3)
    style.configure('CTT.TLabel', background=C_WHITE, foreground=C_ACCENT2, font=('Segoe UI', 11, 'bold'))

    # Entry
    style.configure('TEntry', fieldbackground=C_WHITE, foreground=C_TEXT,
        bordercolor=C_BORDER, insertcolor=C_TEXT, padding=4)
    style.map('TEntry', bordercolor=[('focus', C_ACCENT)])

    # Combobox
    style.configure('TCombobox', fieldbackground=C_WHITE, foreground=C_TEXT,
        bordercolor=C_BORDER, padding=4)
    style.map('TCombobox', bordercolor=[('focus', C_ACCENT)])

    # Buttons
    style.configure('TButton', background=C_ACCENT, foreground=C_WHITE,
        font=FONT_H3, padding=[12, 6], borderwidth=0, relief='flat')
    style.map('TButton',
        background=[('active', C_ACCENT2), ('pressed', C_ACCENT2)])

    style.configure('Secondary.TButton', background=C_BORDER, foreground=C_TEXT,
        font=FONT_BODY, padding=[10, 5], borderwidth=0, relief='flat')
    style.map('Secondary.TButton',
        background=[('active', '#B0BEC5'), ('pressed', '#90A4AE')])

    style.configure('Small.TButton', background=C_ACCENT, foreground=C_WHITE,
        font=FONT_SMALL, padding=[6, 3], borderwidth=0, relief='flat')
    style.map('Small.TButton',
        background=[('active', C_ACCENT2)])

    style.configure('Add.TButton', background='#22C55E', foreground=C_WHITE,
        font=('Segoe UI', 11, 'bold'), padding=[4, 2], borderwidth=0, relief='flat')
    style.map('Add.TButton',
        background=[('active', C_SUCCESS)])

    style.configure('Danger.TButton', background='#EF4444', foreground=C_WHITE,
        font=FONT_SMALL, padding=[6, 3], borderwidth=0, relief='flat')
    style.map('Danger.TButton',
        background=[('active', '#DC2626')])

    style.configure('Link.TButton', background=C_WHITE, foreground=C_ACCENT,
        font=('Segoe UI', 9, 'underline'), padding=[4, 2], borderwidth=0, relief='flat')
    style.map('Link.TButton',
        foreground=[('active', C_ACCENT2)],
        background=[('active', C_WHITE)])

    # Treeview
    style.configure('Treeview',
        background=C_WHITE, fieldbackground=C_WHITE,
        foreground=C_TEXT, font=FONT_BODY,
        rowheight=28, borderwidth=0)
    style.configure('Treeview.Heading',
        background=C_SIDEBAR, foreground=C_WHITE,
        font=FONT_H3, relief='flat', padding=[6, 6])
    style.map('Treeview',
        background=[('selected', C_ACCENT)],
        foreground=[('selected', C_WHITE)])

    # Separator
    style.configure('TSeparator', background=C_BORDER)

    # Scrollbar
    style.configure('TScrollbar',
        background=C_BORDER, troughcolor=C_BG,
        borderwidth=0, arrowsize=12)

    return style


def card_frame(parent, **kwargs):
    f = ttk.Frame(parent, style='Card.TFrame', **kwargs)
    return f


def section_label(parent, text):
    lbl = ttk.Label(parent, text=text, style='H2Card.TLabel')
    return lbl


def field_label(parent, text):
    lbl = ttk.Label(parent, text=text, style='MutedCard.TLabel')
    return lbl
