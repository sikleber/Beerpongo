import "../styles/Field.css"

function Field(props) {
    return (
        <div className="desk">
            <div className="cup-grid">
                <div className="cup-grid-row">
                    <div className={props.dictVal["p1_0_className"]}
                         onClick={props.dictVal["p1_0_OnClick"]}></div>
                    <div className={props.dictVal["p1_1_className"]}
                         onClick={props.dictVal["p1_1_OnClick"]}></div>
                    <div className={props.dictVal["p1_2_className"]}
                         onClick={props.dictVal["p1_2_OnClick"]}></div>
                    <div className={props.dictVal["p1_3_className"]}
                         onClick={props.dictVal["p1_3_OnClick"]}></div>
                </div>
                <div className="cup-grid-row">
                    <div className={props.dictVal["p1_4_className"]}
                         onClick={props.dictVal["p1_4_OnClick"]}></div>
                    <div className={props.dictVal["p1_5_className"]}
                         onClick={props.dictVal["p1_5_OnClick"]}></div>
                    <div className={props.dictVal["p1_6_className"]}
                         onClick={props.dictVal["p1_6_OnClick"]}></div>
                </div>
                <div className="cup-grid-row">
                    <div className={props.dictVal["p1_7_className"]}
                         onClick={props.dictVal["p1_7_OnClick"]}></div>
                    <div className={props.dictVal["p1_8_className"]}
                         onClick={props.dictVal["p1_8_OnClick"]}></div>
                </div>
                <div className="cup-grid-row">
                    <div className={props.dictVal["p1_9_className"]}
                         onClick={props.dictVal["p1_9_OnClick"]}></div>
                </div>
            </div>
            <div className="cup-grid cup-grid-reverse">
                <div className="cup-grid-row">
                    <div className={props.dictVal["p2_0_className"]}
                         onClick={props.dictVal["p2_0_OnClick"]}></div>
                    <div className={props.dictVal["p2_1_className"]}
                         onClick={props.dictVal["p2_1_OnClick"]}></div>
                    <div className={props.dictVal["p2_2_className"]}
                         onClick={props.dictVal["p2_2_OnClick"]}></div>
                    <div className={props.dictVal["p2_3_className"]}
                         onClick={props.dictVal["p2_3_OnClick"]}></div>
                </div>
                <div className="cup-grid-row">
                    <div className={props.dictVal["p2_4_className"]}
                         onClick={props.dictVal["p2_4_OnClick"]}></div>
                    <div className={props.dictVal["p2_5_className"]}
                         onClick={props.dictVal["p2_5_OnClick"]}></div>
                    <div className={props.dictVal["p2_6_className"]}
                         onClick={props.dictVal["p2_6_OnClick"]}></div>
                </div>
                <div className="cup-grid-row">
                    <div className={props.dictVal["p2_7_className"]}
                         onClick={props.dictVal["p2_7_OnClick"]}></div>
                    <div className={props.dictVal["p2_8_className"]}
                         onClick={props.dictVal["p2_8_OnClick"]}></div>
                </div>
                <div className="cup-grid-row">
                    <div className={props.dictVal["p2_9_className"]}
                         onClick={props.dictVal["p2_9_OnClick"]}></div>
                </div>
            </div>
        </div>
    );
}

export default Field;
