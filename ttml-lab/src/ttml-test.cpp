#include <fstream>
#include <iostream>
#include <string>


#include "Jinja2CppLight/Jinja2CppLight.h"

// using J2L = Jinja2CppLight;


namespace J2L = Jinja2CppLight;

J2L::Template template_from_file(const std::string& path)
{
    std::ifstream is(path);
    std::stringstream ss;
    ss << is.rdbuf();
    return std::move(ss.str());
}

int main()
{
    std::cout << "Begin Processing Template..." << std::endl;
    J2L::Template ttml_template("");
    auto the_template(template_from_file("data/template1.jinja-ttml"));
    the_template.setValue("lang", "swe");
    the_template.setValue("cue_count", 2);
    the_template.setValue("cue.start", "00:10");
    the_template.setValue("cue.end", "00:14");
    the_template.setValue("cue.text", "FOURTEEN old");
    the_template.setValue("cue.text", "FOURTEEN");
    the_template.setValue("cue.aux1.aux2.aux3", "lots-of-aux");

    // These have no effect...
    the_template.setValue("cue.text[1]", "-------");
    the_template.setValue("cue[1].text", "-------");
    the_template.setValue("1.text", "-------");
    
    std::cout << the_template.render();

}

