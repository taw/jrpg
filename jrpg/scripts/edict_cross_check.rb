#!/usr/bin/env ruby
$KCODE = 'u'

$edict = {}

File.open("edict").each {|line|
    line.chomp!
    if line =~ /^(\S+?) \[(\S+?)\]/ 
        kanji, reading = $1, $2
        $edict[kanji] ||= [[], []]
        if line =~ /\(P\)/
            $edict[kanji][0].push reading
        else
            $edict[kanji][1].push reading
        end
    end
}

File.open("data/demons-kanji-source.txt").each {|line|
    fields = line.chomp.sub(/^\d+\s+/, "").split(/\t/)
    if fields.size == 1
        # need to split into 2
        kanji = ""
        kana  = ""
        while fields[0] != ""
            case fields[0]
            when /^\((.*?)\|(.*?)\)(.*)/
                kanji += $1
                kana  += $2
                fields[0] = $3
            when /^\[(.*?)\|(.*?)\](.*)/
                kanji += $1
                kana  += $2
                fields[0] = $3
            when /^\*5(.*)/
                kanji += "る"
                kana  += "る"
                fields[0] = $1
            when /^\*(.)(.*)/ # Single Unicode character
                kanji += $1
                kana  += $1
                fields[0] = $2
            when /^\{(.*?)\}(.*)/ # Prefix/suffix - ignore
                fields[0] = $2
            when /^(.)(.*)/  # Single Unicode character
                kanji += $1
                kana  += $1
                fields[0] = $2
            end
        end
        fields = [kanji, kana]
    else
        if fields[0].gsub!(/\*(.)$/,"")
            k = $1
            k = "る" if k == "5"
            fields[0] += k
            fields[1] += k
        end
    end
    kanji, reading = *fields
    reading = reading.sort
    reading_in_edict = $edict[kanji] || [[], []]
    if reading_in_edict[0].size == 0
        reading_in_edict = reading_in_edict[1].sort
    else
        reading_in_edict = reading_in_edict[0].sort
    end

    next if reading == reading_in_edict
    next if reading_in_edict == [] # Well, just some non-existing word
    print "#{kanji}:\n"
    print "    J: #{reading.join(' ')}\n"
    print "    E: #{reading_in_edict.join(' ')}\n"
}
