#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "NLTemplate/NLTemplate.h"



namespace NLT = NL::Template;

std::vector<std::vector<std::string>> the_cues = {{ "00:10", "00:14", "Fourteen"},
                                                  { "00:16", "00:20", "Twenty"},
                                                  { "00:38", "00:42", "Fourty-two"}};

int main()
{
    std::cout << "Begin Processing Template..." << std::endl;

    NLT::LoaderFile loader; // Let's use the default loader that loads files from disk.
    NLT::Template the_template(loader);
    the_template.load( "data/template-NL.jinja-ttml" ); // Load & parse the main template and its dependencies.

    the_template.set("lang", "swe");
    the_template.render(std::cout);

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

