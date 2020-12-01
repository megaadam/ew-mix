#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "NLTemplate/NLTemplate.h"

const std::string mem_template = R"(<?xml version="1.0" encoding="utf-8"?>
<tt xmlns:ttp="http://www.w3.org/ns/ttml#parameter" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling" xmlns:ttm="http://www.w3.org/ns/ttml#metadata"
    xmlns:ebuttm="urn:ebu:metadata" xmlns:ebutts="urn:ebu:style"
    xml:lang="{{ lang }}" xml:space="default"
    ttp:timeBase="media"
    ttp:cellResolution="32 15">
  <head>
    <styling>
      <style xml:id="s0" tts:fontFamily="sansSerif" tts:fontSize="100%" tts:lineHeight="normal"
          tts:color="#FFFFFF" tts:wrapOption="noWrap" tts:textAlign="center"/>
      <style xml:id="s1" tts:color="#ffffff" tts:backgroundColor="#00000040" ebutts:linePadding="0.5c"/>
    </styling>
    <layout>
      <region xml:id="r0" tts:origin="15% 80%" tts:extent="70% 20%" tts:overflow="visible" tts:displayAlign="after"/>
    </layout>
  </head>
  <body style="s0">
    <div region="r0">
    {% block cues %}  <p begin="{{ cue_begin }}" end="{{ cue_end }}"> <span style="s1">{{ cue_text }}</span></p>
    {% endblock %}</div>
  </body>
</tt>
)";


namespace NLT = NL::Template;

std::vector<std::vector<std::string>> the_cues = {{ "00:10", "00:14", "Fourteen"},
                                                  { "00:16", "00:20", "Twenty"},
                                                  { "00:38", "00:42", "Fourty-two"}};

int main()
{
    std::cout << "Begin Processing Template..." << std::endl;

    //NLT::LoaderFile loader; // Let's use the default loader that loads files from disk.
    NLT::LoaderMemory loaderMem;
    loaderMem.add("TEMPLATE", mem_template);
    
    NLT::Template the_template(loaderMem);
//    the_template.load( "data/template-NL.jinja-ttml" ); // Load & parse the main template and its dependencies.
    the_template.load("TEMPLATE"); // Load & parse the main template and its dependencies.

    the_template.set("lang", "swe");

    the_template.block("cues").repeat(the_cues.size());

    unsigned int i = 0;
    for(const auto& cue: the_cues)
    {
        the_template.block("cues")[i].set("cue_begin", cue[0]);
        the_template.block("cues")[i].set("cue_end", cue[1]);
        the_template.block("cues")[i].set("cue_text", cue[2]);
        ++i;
    }

    the_template.render(std::cout);

}

