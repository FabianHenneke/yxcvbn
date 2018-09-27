scoring = require('./scoring')

feedback =
  default_feedback:
    warning: ''
    suggestions: [
      "Verwende mehrere Worte, vermeide bekannte Ausdrücke."
      "Zahlen, Sonderzeichen und Großbuchstaben sind nicht unbedingt notwendig."
    ]

  get_feedback: (score, sequence) ->
    # starting feedback
    return @default_feedback if sequence.length == 0

    # no feedback if score is good or great.
    return if score > 2
      warning: ''
      suggestions: []

    # tie feedback to the longest match for longer sequences
    longest_match = sequence[0]
    for match in sequence[1..]
      longest_match = match if match.token.length > longest_match.token.length
    feedback = @get_match_feedback(longest_match, sequence.length == 1)
    extra_feedback = 'Füge mehr Worte hinzu, am besten seltene.'
    if feedback?
      feedback.suggestions.unshift extra_feedback
      feedback.warning = '' unless feedback.warning?
    else
      feedback =
        warning: ''
        suggestions: [extra_feedback]
    feedback

  get_match_feedback: (match, is_sole_match) ->
    switch match.pattern
      when 'dictionary'
        @get_dictionary_match_feedback match, is_sole_match

      when 'spatial'
        layout = match.graph.toUpperCase()
        warning = if match.turns == 1
          'Tastenreihen sind leicht zu erraten.'
        else
          'Kurze Tastenfolgen sind leicht zu erraten.'
        warning: warning
        suggestions: [
          'Verwende eine längere Tastenfolge mit mehr Richtungswechseln.'
        ]

      when 'repeat'
        warning = if match.base_token.length == 1
          'Wiederholungen wie "aaa" sind leicht zu erraten.'
        else
          'Wiederholungen wie "abcabcabc" sind kaum schwerer zu erraten als "abc".'
        warning: warning
        suggestions: [
          'Vermeide Wiederholungen von Worten und Zeichen.'
        ]

      when 'sequence'
        warning: 'Folgen wie "abc" und "6543" sind leicht zu erraten.'
        suggestions: [
          'Vermeide Folgen.'
        ]

      when 'regex'
        if match.regex_name == 'recent_year'
          warning: 'Nicht lange zurückliegende Jahre sind leicht zu erraten.'
          suggestions: [
            'Vermeide nicht lange zurückliegende Jahre.'
            'Vermeide Jahre, die mit dir in Verbindung gebracht werden könnten.'
          ]

      when 'date'
        warning: 'Daten und Jahreszahlen sind leicht zu erraten.'
        suggestions: [
          'Vermeide Daten und Jahreszahlen, die mit dir in Verbindung gebracht werden können.'
        ]

  get_dictionary_match_feedback: (match, is_sole_match) ->
    warning = if match.dictionary_name == 'passwords'
      if is_sole_match and not match.l33t and not match.reversed
        if match.rank <= 10
          'Dieses Passwort ist unter den 10 meistverwendeten.'
        else if match.rank <= 100
          'Dieses Passwort ist unter den 100 meistverwendeten.'
        else
          'Dies ist ein sehr häufig verwendetes Passwort.'
      else if match.guesses_log10 <= 4
        'Dieses Passwort ist ähnlich zu einem sehr häufig verwendeten.'
    else if match.dictionary_name in ['english_wikipedia', 'german_wikipedia']
      if is_sole_match
        'Ein einzelnes Wort ist leicht zu erraten.'
    else if match.dictionary_name in ['surnames', 'male_names', 'female_names', 'german_given_names', 'german_surnames']
      if is_sole_match
        'Einzelne Namen sind leicht zu erraten.'
      else
        'Häufige Namen sind leicht zu erraten.'
    else
      ''

    suggestions = []
    word = match.token
    if word.match(scoring.START_UPPER)
      suggestions.push "Normale Großschreibung macht ein Passwort kaum sicherer."
    else if word.match(scoring.ALL_UPPER) and word.toLowerCase() != word
      suggestions.push "Komplette Großschreibung ist nicht viel sicherer als Kleinschreibung."

    if match.reversed and match.token.length >= 4
      suggestions.push "Umgedrehte Worte sind nicht viel schwieriger zu erraten."
    if match.l33t
      suggestions.push 'Typische Ersetzungen wie "@" statt "a" helfen nicht viel.'

    result =
      warning: warning
      suggestions: suggestions
    result

module.exports = feedback
