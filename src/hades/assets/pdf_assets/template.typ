
// ===============================================
//  THEME
// ===============================================
#let brand-orange     = rgb("#F48723")
#let brand-red        = rgb("#A32325")
#let brand-dark-red   = rgb("#5C0B14")   // primary
#let brand-highlight  = rgb("#FFE5A3")
#let ink              = rgb("#241012")
#let muted            = rgb("#6E5B5C")
#let paper            = rgb("#FFFFFF")
#let soft-bg          = rgb("#FBF6F1")
#let hairline         = rgb("#EADFD6")

// ---- Fonts ---------------------------------------------------------------
#let body-font = ("Figtree", "Inter", "Helvetica Neue", "Arial")
#let mono-font = ("JetBrains Mono", "DejaVu Sans Mono", "Menlo")

// ===============================================
//  PAGE SETUP
// ===============================================
#set document(title: "@@report_title@@", author: "@@software_name@@ v@@version@@")

#set page(
  paper: "a4",
  margin: (top: 1cm, bottom: 2cm, left: 1cm, right: 1cm),

  background: context {
    if counter(page).get().first() == 1 {
      rect(
        width: 100%,
        height: 100%,
        fill: gradient.radial(
          paper, paper, brand-orange, 
          focal-center: (50%, 100%), radius: 95%
        )
        //radial-gradient(125% 125% at 50% 90%, var(--bg-light) 40%, #e0a237 100%);
      )
    }
  },

  footer: context [
    #set text(8.5pt, fill: muted)
    #line(length: 100%, stroke: 0.5pt + hairline)
    #v(4pt)
    #grid(
      columns: (1fr, 1fr, 1fr),
      align: (left, center, right),
      [@@software_name@@ v@@version@@],
      [@@report_title@@ | @@date_ymd@@],
      [#counter(page).display("1 / 1", both: true)],
    )
  ],
)

#set text(font: body-font, size: 10.5pt, fill: ink, lang: "en")
#set par(justify: true, leading: 0.68em, spacing: 1.1em)

// ===============================================
//  HEADINGS
// ===============================================
#show heading.where(level: 1): it => block(width: 100%, breakable: false)[
  #v(6pt)
  #grid(
    columns: (auto, 1fr),
    gutter: 12pt,
    align: horizon,
    box(
      fill: brand-dark-red,
      radius: 3pt,
      inset: (x: 8pt, y: 6pt),
    )[
      #text(fill: white, weight: 700, size: 12pt)[
        #counter(heading).display()
      ]
    ],
    text(fill: brand-dark-red, weight: 700, size: 16pt)[#it.body],
  )
  #v(2pt)
  #line(length: 100%, stroke: 1.2pt + brand-dark-red)
  #v(6pt)
]

#show heading.where(level: 2): it => block[
  #v(4pt)
  #text(fill: brand-red, weight: 600, size: 12.5pt)[#it.body]
  #v(1pt)
]

#set heading(numbering: "1.")

// ===============================================
//  REUSABLE COMPONENTS
// ===============================================

// --- badge / pill ---------------------------------------------------------
// #let pill(content, bg: brand-highlight, fg: brand-dark-red, outline: false) // = box(
//   fill: bg, radius: 20pt, inset: (x: 9pt, y: 4pt),
//   stroke: if outline { 0.8pt + luma(100) } else { 0pt }
// )[#text(fill: fg, weight: 600, size: 9pt)[#content]]

#let pill(content, bg: brand-highlight, fg: brand-dark-red, outline: false, dest: none, icon: none) = {
  let body = box(
    fill: bg,                    // transparent
    radius: 20pt,
    inset: (x: 9pt, y: 4pt),
    stroke: if outline { 0.8pt + luma(100) } else { 0pt }
  )[
    #set text(size: 9pt, weight: 600, fill: fg)
    #if icon != none { icon } 
    #if icon != none and content != none { h(0.4em) }
    #content
  ]

  if dest != none {
    link(dest, body)
  } else {
    body
  }
}

// --- info card ------------------------------------------------------------
#let card(title, body, accent: brand-dark-red) = block(
  width: 100%,
  fill: soft-bg,
  radius: 6pt,
  stroke: 0.75pt + hairline,
  inset: 12pt,
)[
  #grid(columns: (3pt, 1fr), gutter: 10pt,
    rect(fill: accent, width: 3pt, height: 100%, radius: 2pt),
    [
      #text(fill: accent, weight: 700, size: 10pt)[#upper(title)]
      #v(4pt)
      #body
    ]
  )
]

// --- key/value grid -------------------------------------------------------
#let kv-grid(..pairs) = {
  let items = pairs.pos()
  grid(
    columns: (auto, 1fr),
    row-gutter: 9pt,
    column-gutter: 16pt,
    ..items.map(p => (
      text(fill: muted, weight: 500)[#p.at(0)],
      text(fill: ink, weight: 600)[#p.at(1)],
    )).flatten()
  )
}

// --- styled table ---------------------------------------------------------
#let datatable(columns: 1, caption: none, ..cells) = {
  // Allow figures containing tables to break across page boundaries
  show figure.where(kind: table): set block(breakable: true)

  figure(
    caption: caption,
    kind: table,
    supplement: [Table],
    // Removed clip: true and added breakable: true
    block(
      breakable: true,
      stroke: 0.75pt + hairline,
      table(
        columns: columns,
        inset: (x: 10pt, y: 5pt),
        align: (col, row) => if col == 0 { left } else { center },
        stroke: (x, y) => (
          bottom: if y == 0 { 0pt } else { 0.5pt + hairline }
        ),
        fill: (col, row) => {
          if row == 0 { brand-dark-red }
          else if calc.even(row) { soft-bg }
          else { paper }
        },
        ..cells,
      ),
    ),
  )
}

#show table.cell: it => {
  // Set font size along with text color
  set text(
    size: 9pt, // Change this to your desired size (e.g., 8pt, 10pt, 0.85em)
    fill: if it.y == 0 { paper } else { ink }
  )
  it
}

// --- callout --------------------------------------------------------------
#let callout(body, title: "Note", accent: brand-orange) = block(
  width: 100%,
  fill: accent.lighten(82%),
  radius: 0pt,
  stroke: (left: 3pt + accent),
  inset: 12pt,
)[
  #text(fill: brand-dark-red.darken(15%), weight: 700, size: 9.5pt)[#upper(title)]
  #v(3pt)
  #body
]

// ===============================================
//  HERO SECTION
// ===============================================
#block(
  width: 100%,
  //fill: brand-dark-red,
  radius: 10pt,
  inset: (x: 24pt, y: 22pt),
)[
  #grid(
    columns: (auto, 1fr),
    gutter: 22pt,
    align: horizon,
    // ---- logo (left) ----
    box(
      //fill: white,
      radius: 8pt,
      inset: 12pt,
    )[
      #image("@@logo_path@@", width: 140pt)
    ],
    // ---- title block (right) ----
    [
      #text(fill: ink, weight: 800, size: 26pt)[@@report_title@@]
      #grid(
        columns: (auto, auto, auto),
        column-gutter: 10pt,
        row-gutter: 6pt,
        // TODO: Finalise links
        pill("v@@version@@", bg: none, fg: ink, outline: true,  dest: "https://github.com/Jack6228/Hades/releases/tag/v@@version@@"),
        pill("GitHub", bg: none, fg: ink, outline: true,   dest: "https://github.com/Jack6228/Hades"),
        // TODO: Add DOI link when available
        // pill("Paper", bg: none, fg: ink, outline: true,   dest: "https://doi.org")
      )
      #v(10pt)
      #text(fill: muted.lighten(15%), size: 10pt)[
        Hastie & Smith, et al. (2026)
      ]
    ],
  )
]

#v(4pt)

#callout(title: "Model Configuration")[
  @@overview_text@@
  #v(8pt)
  #kv-grid(
    ("Mode",         [@@mode@@]),
    ("Submode",      [@@submode@@]),
    ("Data suite",   [@@data_suite@@]),
    ($"FeO/Fe"^2^+$,      [@@FeOFe2p@@]),
    ("Stages Run",       @@stages_run@@),
  )
]

#v(16pt)

// ===============================================
//  BODY
// ===============================================

= Results at a Glance

All of the mineral abundances and fractional crystallisation (FC) values for each phase are shown in the table below, as well as the resultant total fractions for the performed amount of fractional crystallisation over all phases.

@@resultsGlanceValue@@

@@resultsGlanceTable@@

= Parameter Configuration

The parameters below define the model as it was executed for this run.

@@KDvalues@@

#v(6pt)

= Magma Evolution

== Initial Compositions

@@initial_magma@@

== Computed Compositions

@@computed_magma@@

= Optimisation Results

@@phase_results@@

#v(8pt)

= Figures

@@figures_block@@

#v(20pt)
#line(length: 100%, stroke: 0.5pt + hairline)
#v(4pt)
#align(center)[
  #text(size: 8.5pt, fill: muted)[
    Generated automatically by @@software_name@@ v@@version@@ | @@date_ymdhms@@
  ]
]
